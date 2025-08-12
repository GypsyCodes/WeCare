"""
Authentication endpoints
"""
from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.models import Usuario, PerfilEnum, StatusUsuarioEnum
from app.core.security import SecurityUtils, verify_password, get_password_hash
from app.core.config import settings
from app.core.deps import get_current_user, verify_registration_token, log_action
from app.schemas.usuario import (
    LoginRequest, Token, UsuarioResponse, TokenValidationResponse,
    UsuarioRegistrationComplete
)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint - authenticate user and return JWT token
    """
    # Get user by email
    result = await db.execute(
        select(Usuario).where(Usuario.email == login_data.email)
    )
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if not user or not user.senha_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(login_data.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if user.status != StatusUsuarioEnum.ATIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token with additional claims
    additional_claims = {
        "perfil": user.perfil.value,
        "email": user.email
    }
    
    access_token = SecurityUtils.create_access_token(
        subject=user.id,
        additional_claims=additional_claims
    )
    
    # Log login action
    await log_action(
        request=request,
        current_user=user,
        action="LOGIN",
        db=db
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UsuarioResponse.from_orm(user)
    )


@router.post("/validate-token", response_model=TokenValidationResponse)
async def validate_token(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Validate JWT token and return user info
    """
    return TokenValidationResponse(
        valid=True,
        user_id=current_user.id,
        email=current_user.email,
        perfil=current_user.perfil
    )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh JWT token
    """
    # Create new access token
    additional_claims = {
        "perfil": current_user.perfil.value,
        "email": current_user.email
    }
    
    access_token = SecurityUtils.create_access_token(
        subject=current_user.id,
        additional_claims=additional_claims
    )
    
    # Log token refresh
    await log_action(
        request=request,
        current_user=current_user,
        action="TOKEN_REFRESH",
        db=db
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UsuarioResponse.from_orm(current_user)
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout endpoint (mainly for logging purposes)
    """
    # Log logout action
    await log_action(
        request=request,
        current_user=current_user,
        action="LOGOUT",
        db=db
    )
    
    return {"message": "Successfully logged out"}


@router.get("/registration/{token}")
async def get_registration_info(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user info for registration completion
    """
    # Verify registration token
    token_data = await verify_registration_token(token, db)
    user = token_data["user"]
    
    return {
        "user_id": user.id,
        "nome": user.nome,
        "email": user.email,
        "cpf": user.cpf,
        "perfil": user.perfil.value
    }


@router.post("/complete-registration/{token}")
async def complete_registration(
    token: str,
    registration_data: UsuarioRegistrationComplete,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete user registration with password and additional info
    """
    # Verify registration token
    token_data = await verify_registration_token(token, db)
    user = token_data["user"]
    
    # Check if user is already registered (has password)
    if user.senha_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration already completed"
        )
    
    # Update user with registration data
    user.senha_hash = get_password_hash(registration_data.senha)
    user.token = None  # Clear registration token
    
    # Update additional user data if provided
    if registration_data.telefone:
        if not user.documentos:
            user.documentos = {}
        user.documentos["telefone"] = registration_data.telefone
    
    if registration_data.endereco:
        if not user.documentos:
            user.documentos = {}
        user.documentos["endereco"] = registration_data.endereco
    
    if registration_data.dados_profissionais:
        if not user.documentos:
            user.documentos = {}
        user.documentos["dados_profissionais"] = registration_data.dados_profissionais
    
    await db.commit()
    await db.refresh(user)
    
    # Log registration completion
    await log_action(
        request=request,
        current_user=user,
        action="REGISTRATION_COMPLETED",
        resource="Usuario",
        resource_id=user.id,
        db=db
    )
    
    # Create access token for immediate login
    additional_claims = {
        "perfil": user.perfil.value,
        "email": user.email
    }
    
    access_token = SecurityUtils.create_access_token(
        subject=user.id,
        additional_claims=additional_claims
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UsuarioResponse.from_orm(user)
    )


@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Get current user information
    """
    return UsuarioResponse.from_orm(current_user) 