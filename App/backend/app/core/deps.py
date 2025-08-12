"""
Dependency functions for FastAPI
"""
from typing import Optional, Dict, Any
import json
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import SecurityUtils
from app.core.models import Usuario, PerfilEnum, Log
from app.schemas.usuario import TokenData


# Security scheme
security = HTTPBearer()


def serialize_for_json(obj):
    """
    Convert objects to JSON-serializable format
    """
    from datetime import date, datetime, time
    
    if hasattr(obj, 'value'):  # Enum objects
        return obj.value
    elif isinstance(obj, (date, datetime)):  # Date and datetime objects
        return obj.isoformat()
    elif isinstance(obj, time):  # Time objects
        return obj.strftime('%H:%M:%S')
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Usuario:
    """
    Get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token
        payload = SecurityUtils.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        # Check token type
        if payload.get("type") != "access":
            raise credentials_exception
        
        # Get user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database
        result = await db.execute(
            select(Usuario).where(Usuario.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        
        # Check if user is active
        if user.status.value != "Ativo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        return user
        
    except Exception as e:
        raise credentials_exception


def require_admin():
    """
    Dependency factory that requires admin privileges
    """
    def check_admin(current_user: Usuario = Depends(get_current_user)):
        if current_user.perfil != PerfilEnum.ADMINISTRADOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return current_user
    return check_admin


def require_supervisor():
    """
    Dependency factory that requires supervisor or admin privileges
    """
    def check_supervisor(current_user: Usuario = Depends(get_current_user)):
        if current_user.perfil not in [PerfilEnum.ADMINISTRADOR, PerfilEnum.SUPERVISOR]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Supervisor or admin privileges required"
            )
        return current_user
    return check_supervisor


async def verify_registration_token(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify registration token and return payload
    """
    token_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired registration token"
    )
    
    try:
        # Verify token
        payload = SecurityUtils.verify_token(token)
        if payload is None:
            raise token_exception
        
        # Check token type
        if payload.get("type") != "registration":
            raise token_exception
        
        # Get user ID from token
        user_id = payload.get("sub")
        if user_id is None:
            raise token_exception
        
        # Verify user exists and token matches
        result = await db.execute(
            select(Usuario).where(Usuario.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if user is None or user.token != token:
            raise token_exception
        
        return {
            "user_id": user.id,
            "user": user,
            "payload": payload
        }
        
    except Exception:
        raise token_exception


async def log_action(
    request: Request,
    current_user: Optional[Usuario],
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    db: AsyncSession = None
):
    """
    Log user actions
    """
    # Extract client info
    client_host = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Build description
    descricao = action
    if resource:
        descricao = f"{action} - {resource}"
        if resource_id:
            descricao += f" (ID: {resource_id})"
    
    # Prepare extra data - serialize enums to avoid JSON serialization errors
    dados_extras = {}
    if details:
        dados_extras.update(serialize_for_json(details))
    
    if resource:
        dados_extras['recurso'] = resource
    if resource_id:
        dados_extras['recurso_id'] = resource_id
    
    # Create log entry with correct fields
    log_entry = Log(
        usuario_id=current_user.id if current_user else None,
        acao=action,
        descricao=descricao,
        ip_address=client_host,
        user_agent=user_agent,
        dados_extras=dados_extras if dados_extras else None
    )
    
    db.add(log_entry)
    await db.commit()


class PermissionChecker:
    """
    Class to check various permissions
    """
    
    @staticmethod
    def can_manage_users(user: Usuario) -> bool:
        """Check if user can manage other users"""
        return user.perfil in [PerfilEnum.ADMINISTRADOR]
    
    @staticmethod
    def can_manage_escalas(user: Usuario) -> bool:
        """Check if user can manage schedules"""
        return user.perfil in [PerfilEnum.ADMINISTRADOR, PerfilEnum.SUPERVISOR]
    
    @staticmethod
    def can_view_reports(user: Usuario) -> bool:
        """Check if user can view reports"""
        return user.perfil in [PerfilEnum.ADMINISTRADOR, PerfilEnum.SUPERVISOR]
    
    @staticmethod
    def can_manage_user_data(current_user: Usuario, target_user_id: int) -> bool:
        """Check if user can manage another user's data"""
        # Admin can manage anyone
        if current_user.perfil == PerfilEnum.ADMINISTRADOR:
            return True
        
        # Users can manage their own data
        if current_user.id == target_user_id:
            return True
        
        return False
    
    @staticmethod
    def can_perform_checkin(user: Usuario, escala_usuario_id: int) -> bool:
        """Check if user can perform check-in for a schedule"""
        # Admin and supervisors can check-in for anyone
        if user.perfil in [PerfilEnum.ADMINISTRADOR, PerfilEnum.SUPERVISOR]:
            return True
        
        # Users can only check-in for their own schedules
        return user.id == escala_usuario_id 