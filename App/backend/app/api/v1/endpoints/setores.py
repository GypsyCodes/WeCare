"""
Setor management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import Setor
from app.core.deps import get_current_user, require_supervisor, log_action
from app.schemas.setor import (
    SetorResponse, SetorCreate, SetorUpdate, SetorListResponse
)

router = APIRouter()


@router.get("/", response_model=SetorListResponse)
async def list_setores(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    ativo: bool = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List setores with pagination and filters
    """
    # Build base query
    query = select(Setor)
    
    # Apply filters
    if ativo is not None:
        query = query.where(Setor.ativo == ativo)
    
    # Count total
    count_query = select(func.count(Setor.id))
    if ativo is not None:
        count_query = count_query.where(Setor.ativo == ativo)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    query = query.order_by(Setor.nome.asc())
    
    # Execute query
    result = await db.execute(query)
    setores = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_SETORES",
        details={"page": page, "per_page": per_page, "ativo": ativo},
        db=db
    )
    
    # Calculate pagination
    pages = (total + per_page - 1) // per_page
    
    return SetorListResponse(
        setores=[SetorResponse.from_orm(setor) for setor in setores],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages
    )


@router.get("/ativos", response_model=List[SetorResponse])
async def list_setores_ativos(
    request: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List only active setores (for dropdowns)
    """
    # Get active setores
    query = select(Setor).where(Setor.ativo == True).order_by(Setor.nome.asc())
    result = await db.execute(query)
    setores = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_SETORES_ATIVOS",
        db=db
    )
    
    return [SetorResponse.from_orm(setor) for setor in setores]


@router.get("/{setor_id}", response_model=SetorResponse)
async def get_setor(
    setor_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get setor by ID
    """
    # Get setor
    result = await db.execute(select(Setor).where(Setor.id == setor_id))
    setor = result.scalar_one_or_none()
    
    if not setor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setor not found"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_SETOR",
        resource="Setor",
        resource_id=setor_id,
        db=db
    )
    
    return SetorResponse.from_orm(setor)


@router.post("/", response_model=SetorResponse)
async def create_setor(
    setor_data: SetorCreate,
    request: Request,
    current_user = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new setor
    Only supervisors and admins can create setores
    """
    # Check if setor with same name already exists in the same establishment
    result = await db.execute(
        select(Setor).where(
            Setor.nome == setor_data.nome.upper(),
            Setor.estabelecimento_id == setor_data.estabelecimento_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setor with this name already exists in this establishment"
        )
    
    # Create setor (convert name to uppercase)
    novo_setor = Setor(
        nome=setor_data.nome.upper(),
        descricao=setor_data.descricao,
        estabelecimento_id=setor_data.estabelecimento_id,
        ativo=setor_data.ativo
    )
    
    db.add(novo_setor)
    await db.commit()
    await db.refresh(novo_setor)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="CREATE_SETOR",
        resource="Setor",
        resource_id=novo_setor.id,
        details=setor_data.dict(),
        db=db
    )
    
    return SetorResponse.from_orm(novo_setor)


@router.put("/{setor_id}", response_model=SetorResponse)
async def update_setor(
    setor_id: int,
    setor_data: SetorUpdate,
    request: Request,
    current_user = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update setor
    Only supervisors and admins can update setores
    """
    # Get setor
    result = await db.execute(select(Setor).where(Setor.id == setor_id))
    setor = result.scalar_one_or_none()
    
    if not setor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setor not found"
        )
    
    # Check if new name conflicts with existing setor
    if setor_data.nome:
        result = await db.execute(
            select(Setor).where(
                Setor.nome == setor_data.nome.upper(),
                Setor.id != setor_id
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Setor with this name already exists"
            )
    
    # Update fields
    update_data = setor_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'nome' and value:
            setattr(setor, field, value.upper())
        elif hasattr(setor, field):
            setattr(setor, field, value)
    
    await db.commit()
    await db.refresh(setor)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="UPDATE_SETOR",
        resource="Setor",
        resource_id=setor_id,
        details=update_data,
        db=db
    )
    
    return SetorResponse.from_orm(setor)


@router.delete("/{setor_id}")
async def delete_setor(
    setor_id: int,
    request: Request,
    current_user = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete setor
    Only supervisors and admins can delete setores
    """
    # Get setor
    result = await db.execute(select(Setor).where(Setor.id == setor_id))
    setor = result.scalar_one_or_none()
    
    if not setor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setor not found"
        )
    
    # Check if setor is being used in any escala_usuarios
    from app.core.models import escala_usuarios
    result = await db.execute(
        select(escala_usuarios).where(escala_usuarios.c.setor_id == setor_id)
    )
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete setor that is being used in schedules"
        )
    
    # Delete setor
    await db.delete(setor)
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="DELETE_SETOR",
        resource="Setor",
        resource_id=setor_id,
        db=db
    )
    
    return {"message": "Setor deleted successfully"} 