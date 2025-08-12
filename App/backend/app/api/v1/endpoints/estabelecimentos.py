"""
Estabelecimento management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import Estabelecimento, Usuario
from app.core.deps import (
    get_current_user, require_admin, require_supervisor, 
    PermissionChecker, log_action
)
from app.schemas.estabelecimento import (
    EstabelecimentoResponse, EstabelecimentoCreate, EstabelecimentoUpdate, 
    EstabelecimentoList
)

router = APIRouter()


@router.get("/", response_model=EstabelecimentoList)
async def list_estabelecimentos(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List estabelecimentos with pagination and filters
    """
    # Build query
    query = select(Estabelecimento)
    
    # Apply filters
    conditions = []
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Estabelecimento.nome.ilike(search_term),
                Estabelecimento.endereco.ilike(search_term)
            )
        )
    
    if ativo is not None:
        conditions.append(Estabelecimento.ativo == ativo)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count total
    count_query = select(func.count()).select_from(Estabelecimento)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset((page - 1) * size).limit(size)
    query = query.order_by(Estabelecimento.nome)
    
    result = await db.execute(query)
    estabelecimentos = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_ESTABELECIMENTOS",
        details={"filters": {"search": search, "ativo": ativo}},
        db=db
    )
    
    return EstabelecimentoList(
        estabelecimentos=estabelecimentos,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{estabelecimento_id}", response_model=EstabelecimentoResponse)
async def get_estabelecimento(
    estabelecimento_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific estabelecimento by ID
    """
    query = select(Estabelecimento).where(Estabelecimento.id == estabelecimento_id)
    result = await db.execute(query)
    estabelecimento = result.scalar_one_or_none()
    
    if not estabelecimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="GET_ESTABELECIMENTO",
        resource="estabelecimento",
        resource_id=estabelecimento_id,
        db=db
    )
    
    return estabelecimento


@router.post("/", response_model=EstabelecimentoResponse)
async def create_estabelecimento(
    estabelecimento_data: EstabelecimentoCreate,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new estabelecimento
    Requires admin privileges
    """
    # Check if estabelecimento with same name already exists
    existing_query = select(Estabelecimento).where(
        Estabelecimento.nome == estabelecimento_data.nome
    )
    existing_result = await db.execute(existing_query)
    existing_estabelecimento = existing_result.scalar_one_or_none()
    
    if existing_estabelecimento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estabelecimento com este nome já existe"
        )
    
    # Create new estabelecimento
    estabelecimento = Estabelecimento(**estabelecimento_data.model_dump())
    db.add(estabelecimento)
    await db.commit()
    await db.refresh(estabelecimento)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="CREATE_ESTABELECIMENTO",
        resource="estabelecimento",
        resource_id=estabelecimento.id,
        details={"nome": estabelecimento.nome, "endereco": estabelecimento.endereco},
        db=db
    )
    
    return estabelecimento


@router.put("/{estabelecimento_id}", response_model=EstabelecimentoResponse)
async def update_estabelecimento(
    estabelecimento_id: int,
    estabelecimento_data: EstabelecimentoUpdate,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update estabelecimento
    Requires admin privileges
    """
    # Get estabelecimento
    query = select(Estabelecimento).where(Estabelecimento.id == estabelecimento_id)
    result = await db.execute(query)
    estabelecimento = result.scalar_one_or_none()
    
    if not estabelecimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )
    
    # Check if name is being changed and if it conflicts
    if estabelecimento_data.nome and estabelecimento_data.nome != estabelecimento.nome:
        existing_query = select(Estabelecimento).where(
            and_(
                Estabelecimento.nome == estabelecimento_data.nome,
                Estabelecimento.id != estabelecimento_id
            )
        )
        existing_result = await db.execute(existing_query)
        existing_estabelecimento = existing_result.scalar_one_or_none()
        
        if existing_estabelecimento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estabelecimento com este nome já existe"
            )
    
    # Update estabelecimento
    update_data = estabelecimento_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(estabelecimento, field, value)
    
    await db.commit()
    await db.refresh(estabelecimento)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="UPDATE_ESTABELECIMENTO",
        resource="estabelecimento",
        resource_id=estabelecimento_id,
        details=update_data,
        db=db
    )
    
    return estabelecimento


@router.delete("/{estabelecimento_id}")
async def delete_estabelecimento(
    estabelecimento_id: int,
    request: Request,
    current_user: Usuario = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete estabelecimento (soft delete - set ativo=False)
    Requires admin privileges
    """
    # Get estabelecimento
    query = select(Estabelecimento).where(Estabelecimento.id == estabelecimento_id)
    result = await db.execute(query)
    estabelecimento = result.scalar_one_or_none()
    
    if not estabelecimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )
    
    # Check if estabelecimento has active escalas
    from app.core.models import Escala, StatusEscalaEnum
    escalas_query = select(func.count()).select_from(Escala).where(
        and_(
            Escala.estabelecimento_id == estabelecimento_id,
            Escala.status.in_([StatusEscalaEnum.PENDENTE, StatusEscalaEnum.CONFIRMADO])
        )
    )
    escalas_result = await db.execute(escalas_query)
    active_escalas = escalas_result.scalar()
    
    if active_escalas > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir estabelecimento com {active_escalas} escalas ativas"
        )
    
    # Soft delete
    estabelecimento.ativo = False
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="DELETE_ESTABELECIMENTO",
        resource="estabelecimento",
        resource_id=estabelecimento_id,
        details={"nome": estabelecimento.nome},
        db=db
    )
    
    return {"message": "Estabelecimento desativado com sucesso"}


@router.get("/{estabelecimento_id}/escalas")
async def get_estabelecimento_escalas(
    estabelecimento_id: int,
    request: Request,
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get escalas for specific estabelecimento
    """
    # Verify estabelecimento exists
    estabelecimento_query = select(Estabelecimento).where(
        Estabelecimento.id == estabelecimento_id
    )
    estabelecimento_result = await db.execute(estabelecimento_query)
    estabelecimento = estabelecimento_result.scalar_one_or_none()
    
    if not estabelecimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estabelecimento não encontrado"
        )
    
    # Import here to avoid circular imports
    from app.core.models import Escala
    from datetime import datetime, date
    
    # Build escalas query
    escalas_query = select(Escala).where(Escala.estabelecimento_id == estabelecimento_id)
    escalas_query = escalas_query.options(
        selectinload(Escala.usuario),
        selectinload(Escala.estabelecimento)
    )
    
    # Apply date filters
    if data_inicio:
        try:
            data_inicio_parsed = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            escalas_query = escalas_query.where(Escala.data_fim >= data_inicio_parsed)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data_inicio inválido. Use YYYY-MM-DD"
            )
    
    if data_fim:
        try:
            data_fim_parsed = datetime.strptime(data_fim, "%Y-%m-%d").date()
            escalas_query = escalas_query.where(Escala.data_inicio <= data_fim_parsed)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de data_fim inválido. Use YYYY-MM-DD"
            )
    
    escalas_result = await db.execute(escalas_query)
    escalas = escalas_result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="GET_ESTABELECIMENTO_ESCALAS",
        resource="estabelecimento",
        resource_id=estabelecimento_id,
        details={"data_inicio": data_inicio, "data_fim": data_fim},
        db=db
    )
    
    return {
        "estabelecimento": estabelecimento,
        "escalas": escalas,
        "total": len(escalas)
    } 