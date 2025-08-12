"""
User management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import Usuario, PerfilEnum, StatusUsuarioEnum
from app.core.deps import (
    get_current_user, require_admin, require_supervisor, 
    PermissionChecker, log_action
)
from app.core.security import SecurityUtils, get_password_hash
from app.schemas.usuario import (
    UsuarioResponse, UsuarioCreate, UsuarioUpdate, UsuarioListResponse,
    UsuarioChangePassword
)

router = APIRouter()


@router.get("/", response_model=UsuarioListResponse)
async def list_usuarios(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    perfil: Optional[PerfilEnum] = Query(None),
    status: Optional[StatusUsuarioEnum] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List users with pagination and filters
    Requires supervisor or admin privileges
    """
    # Build query
    query = select(Usuario)
    
    # Apply filters
    conditions = []
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Usuario.nome.ilike(search_term),
                Usuario.email.ilike(search_term),
                Usuario.cpf.ilike(search_term)
            )
        )
    
    if perfil:
        conditions.append(Usuario.perfil == perfil)
    
    if status:
        conditions.append(Usuario.status == status)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count total
    count_query = select(func.count(Usuario.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    query = query.order_by(Usuario.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    usuarios = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_USUARIOS",
        details={"filters": {"search": search, "perfil": perfil, "status": status}},
        db=db
    )
    
    # Calculate pagination
    pages = (total + per_page - 1) // per_page
    
    return UsuarioListResponse(
        users=[UsuarioResponse.from_orm(user) for user in usuarios],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/{user_id}", response_model=UsuarioResponse)
async def get_usuario(
    user_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID
    Users can only view their own data unless they are admin/supervisor
    """
    # Check permissions
    if not PermissionChecker.can_manage_user_data(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user"
        )
    
    # Get user
    result = await db.execute(
        select(Usuario).where(Usuario.id == user_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_USUARIO",
        resource="Usuario",
        resource_id=user_id,
        db=db
    )
    
    return UsuarioResponse.from_orm(usuario)


@router.post("/", response_model=UsuarioResponse)
async def create_usuario(
    user_data: UsuarioCreate,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new user (pre-registration)
    Only admins can create users
    """
    # Check if email already exists
    result = await db.execute(
        select(Usuario).where(Usuario.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if CPF already exists
    result = await db.execute(
        select(Usuario).where(Usuario.cpf == user_data.cpf)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF already registered"
        )
    
    # Generate registration token
    registration_token = SecurityUtils.generate_secure_token()
    
    # Create user
    novo_usuario = Usuario(
        nome=user_data.nome,
        email=user_data.email,
        cpf=user_data.cpf,
        perfil=user_data.perfil,
        token=registration_token,
        status=StatusUsuarioEnum.ATIVO
    )
    
    db.add(novo_usuario)
    await db.commit()
    await db.refresh(novo_usuario)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="CREATE_USUARIO",
        resource="Usuario",
        resource_id=novo_usuario.id,
        details={"email": user_data.email, "perfil": user_data.perfil.value},
        db=db
    )
    
    # TODO: Send registration email with token
    # await send_registration_email(novo_usuario.email, registration_token)
    
    return UsuarioResponse.from_orm(novo_usuario)


@router.put("/{user_id}", response_model=UsuarioResponse)
async def update_usuario(
    user_id: int,
    user_data: UsuarioUpdate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user data
    Users can update their own data, admins can update anyone
    """
    # Check permissions
    if not PermissionChecker.can_manage_user_data(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
    
    # Get user
    result = await db.execute(
        select(Usuario).where(Usuario.id == user_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check email uniqueness if changing
    if user_data.email and user_data.email != usuario.email:
        result = await db.execute(
            select(Usuario).where(
                and_(Usuario.email == user_data.email, Usuario.id != user_id)
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(usuario, field):
            setattr(usuario, field, value)
    
    await db.commit()
    await db.refresh(usuario)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="UPDATE_USUARIO",
        resource="Usuario",
        resource_id=user_id,
        details=update_data,
        db=db
    )
    
    return UsuarioResponse.from_orm(usuario)


@router.post("/{user_id}/change-password")
async def change_password(
    user_id: int,
    password_data: UsuarioChangePassword,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    Users can only change their own password
    """
    # Only users can change their own password
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only change your own password"
        )
    
    # Verify current password
    if not current_user.senha_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no password set"
        )
    
    from app.core.security import verify_password
    if not verify_password(password_data.senha_atual, current_user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.senha_hash = get_password_hash(password_data.nova_senha)
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="CHANGE_PASSWORD",
        resource="Usuario",
        resource_id=user_id,
        db=db
    )
    
    return {"message": "Password changed successfully"}


@router.post("/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle user active/inactive status
    Only admins can change user status
    """
    # Get user
    result = await db.execute(
        select(Usuario).where(Usuario.id == user_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deactivating yourself
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own status"
        )
    
    # Toggle status
    new_status = (
        StatusUsuarioEnum.INATIVO 
        if usuario.status == StatusUsuarioEnum.ATIVO 
        else StatusUsuarioEnum.ATIVO
    )
    usuario.status = new_status
    
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="TOGGLE_USER_STATUS",
        resource="Usuario",
        resource_id=user_id,
        details={"new_status": new_status.value},
        db=db
    )
    
    return {
        "message": f"User status changed to {new_status.value}",
        "status": new_status.value
    }


@router.delete("/{user_id}")
async def delete_usuario(
    user_id: int,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user (soft delete by setting inactive)
    Only admins can delete users
    """
    # Get user
    result = await db.execute(
        select(Usuario).where(Usuario.id == user_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deleting yourself
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    # Soft delete - just set inactive
    usuario.status = StatusUsuarioEnum.INATIVO
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="DELETE_USUARIO",
        resource="Usuario",
        resource_id=user_id,
        details={"email": usuario.email},
        db=db
    )
    
    return {"message": "User deleted successfully"}


@router.get("/{user_id}/registration-token")
async def regenerate_registration_token(
    user_id: int,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate registration token for user who hasn't completed registration
    Only admins can regenerate tokens
    """
    # Get user
    result = await db.execute(
        select(Usuario).where(Usuario.id == user_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user already completed registration
    if usuario.senha_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already completed registration"
        )
    
    # Generate new token
    new_token = SecurityUtils.generate_secure_token()
    usuario.token = new_token
    
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="REGENERATE_TOKEN",
        resource="Usuario",
        resource_id=user_id,
        db=db
    )
    
    return {
        "message": "Registration token regenerated",
        "token": new_token,
        "registration_url": f"/auth/registration/{new_token}"
    } 