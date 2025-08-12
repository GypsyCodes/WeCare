"""
Schedule (Escala) management endpoints
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, between
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import (
    Escala, Usuario, StatusEscalaEnum, PerfilEnum, StatusUsuarioEnum,
    TransferenciaPlantao, Checkin, escala_usuarios, Estabelecimento
)
from app.core.deps import (
    get_current_user, require_supervisor, PermissionChecker, log_action
)
from app.schemas.escala import (
    EscalaResponse, EscalaCreate, EscalaUpdate, EscalaListResponse,
    EscalaFilter, EscalaStats, EscalaCalendarView, EscalaBulkCreate,
    EscalaBulkUpdate
)

router = APIRouter()


@router.get("/supervisores/disponiveis", response_model=List[dict])
async def list_supervisores_disponiveis(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List available supervisors for assignment to schedules
    """
    # Get all active supervisors and administrators
    result = await db.execute(
        select(Usuario).where(
            Usuario.perfil.in_([PerfilEnum.SUPERVISOR, PerfilEnum.ADMINISTRADOR]),
            Usuario.status == StatusUsuarioEnum.ATIVO
        ).order_by(Usuario.nome.asc())
    )
    supervisores = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_SUPERVISORES_DISPONIVEIS",
        db=db
    )
    
    return [
        {
            "id": s.id,
            "nome": s.nome,
            "email": s.email,
            "perfil": s.perfil.value
        }
        for s in supervisores
    ]


@router.get("/setores/disponiveis", response_model=List[dict])
async def list_setores_disponiveis(
    request: Request,
    estabelecimento_id: Optional[int] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List available setores for assignment to users in schedules
    """
    # Get active setores for specific establishment or all if not specified
    from app.core.models import Setor
    query = select(Setor).where(Setor.ativo == True)
    
    if estabelecimento_id:
        query = query.where(Setor.estabelecimento_id == estabelecimento_id)
    
    query = query.order_by(Setor.nome.asc())
    result = await db.execute(query)
    setores = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_SETORES_DISPONIVEIS",
        db=db
    )
    
    return [
        {
            "id": s.id,
            "nome": s.nome,
            "descricao": s.descricao,
            "estabelecimento_id": s.estabelecimento_id
        }
        for s in setores
    ]


@router.get("/", response_model=EscalaListResponse)
async def list_escalas(
    request: Request,
    filter_params: EscalaFilter = Depends(),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List schedules with pagination and filters
    Sócios can only see their own schedules
    """
    # Build base query
    query = select(Escala).options(selectinload(Escala.estabelecimento))
    
    # Apply user restrictions
    conditions = []
    if current_user.perfil == PerfilEnum.SOCIO:
        # For SOCIO, we need to check if they are assigned to any scales
        # This will be handled after getting the scales
        pass
    elif filter_params.usuario_id:
        # For other users, we'll filter by usuario_id in escala_usuarios
        # This will be handled after getting the scales
        pass
    
    # Apply date filters
    if filter_params.data_inicio:
        conditions.append(Escala.data_inicio >= filter_params.data_inicio)
    
    if filter_params.data_fim:
        conditions.append(Escala.data_inicio <= filter_params.data_fim)
    
    # Apply status filter
    if filter_params.status:
        conditions.append(Escala.status == filter_params.status)
    
    # Apply establishment filter
    if filter_params.estabelecimento_id:
        conditions.append(Escala.estabelecimento_id == filter_params.estabelecimento_id)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count total
    count_query = select(func.count(Escala.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (filter_params.page - 1) * filter_params.per_page
    query = query.offset(offset).limit(filter_params.per_page)
    query = query.order_by(Escala.data_inicio.desc(), Escala.hora_inicio.asc())
    
    # Execute query
    result = await db.execute(query)
    escalas = result.scalars().all()
    
    # Get usuarios_atribuidos for all scales
    escala_ids = [escala.id for escala in escalas]
    escala_usuarios_data = {}
    
    if escala_ids:
        # Get escala_usuarios relationships
        escala_usuarios_query = select(escala_usuarios).where(escala_usuarios.c.escala_id.in_(escala_ids))
        escala_usuarios_result = await db.execute(escala_usuarios_query)
        escala_usuarios_rows = escala_usuarios_result.fetchall()
        
        # Get user data for escala_usuarios
        usuario_ids = [row.usuario_id for row in escala_usuarios_rows]
        if usuario_ids:
            usuarios_query = select(Usuario).where(Usuario.id.in_(usuario_ids))
            usuarios_result = await db.execute(usuarios_query)
            usuarios_dict = {u.id: u for u in usuarios_result.scalars().all()}
            
            # Group escala_usuarios by escala_id
            for row in escala_usuarios_rows:
                if row.escala_id not in escala_usuarios_data:
                    escala_usuarios_data[row.escala_id] = []
                usuario = usuarios_dict.get(row.usuario_id)
                escala_usuarios_data[row.escala_id].append({
                    "id": row.id,
                    "usuario_id": row.usuario_id,
                    "setor": row.setor,
                    "status": row.status,
                    "usuario": {
                        "id": usuario.id,
                        "nome": usuario.nome,
                        "email": usuario.email,
                        "perfil": usuario.perfil.value
                    } if usuario else None
                })
    
    # Filter scales based on user restrictions
    filtered_escalas = []
    for escala in escalas:
        usuarios_atribuidos = escala_usuarios_data.get(escala.id, [])
        
        # Apply user restrictions
        if current_user.perfil == PerfilEnum.SOCIO:
            # SOCIO can only see scales they are assigned to
            if not any(u["usuario_id"] == current_user.id for u in usuarios_atribuidos):
                continue
        elif filter_params.usuario_id:
            # Filter by specific user
            if not any(u["usuario_id"] == filter_params.usuario_id for u in usuarios_atribuidos):
                continue
        
        # Create escala response with usuarios_atribuidos
        escala_dict = {
            "id": escala.id,
            "data_inicio": escala.data_inicio,
            "data_fim": escala.data_fim,
            "hora_inicio": escala.hora_inicio,
            "hora_fim": escala.hora_fim,
            "estabelecimento_id": escala.estabelecimento_id,
            "status": escala.status,
            "observacoes": escala.observacoes,
            "created_at": escala.created_at,
            "updated_at": escala.updated_at,
            "estabelecimento": {
                "id": escala.estabelecimento.id,
                "nome": escala.estabelecimento.nome,
                "endereco": escala.estabelecimento.endereco
            } if escala.estabelecimento else None,
            "usuarios_atribuidos": usuarios_atribuidos
        }
        filtered_escalas.append(escala_dict)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_ESCALAS",
        details={"filters": filter_params.dict()},
        db=db
    )
    
    # Calculate pagination
    pages = (total + filter_params.per_page - 1) // filter_params.per_page
    
    return EscalaListResponse(
        escalas=filtered_escalas,
        total=len(filtered_escalas),
        page=filter_params.page,
        per_page=filter_params.per_page,
        pages=pages
    )


@router.get("/calendar", response_model=List[EscalaCalendarView])
async def get_calendar_view(
    request: Request,
    start_date: date = Query(...),
    end_date: date = Query(...),
    usuario_id: Optional[int] = Query(None),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get calendar view of schedules for a date range
    """
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Limit to 31 days
    if (end_date - start_date).days > 31:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 31 days"
        )
    
    # Apply user restrictions
    conditions = [
        Escala.data_inicio >= start_date,
        Escala.data_inicio <= end_date
    ]
    
    if current_user.perfil == PerfilEnum.SOCIO:
        conditions.append(Escala.usuario_id == current_user.id)
    elif usuario_id:
        conditions.append(Escala.usuario_id == usuario_id)
    
    # Get schedules
    query = select(Escala).options(selectinload(Escala.estabelecimento)).where(and_(*conditions))
    result = await db.execute(query)
    escalas = result.scalars().all()
    
    # Get users for each scale
    escala_ids = [escala.id for escala in escalas]
    escala_usuarios_data = {}
    
    if escala_ids:
        # Get escala_usuarios relationships
        escala_usuarios_query = select(escala_usuarios).where(escala_usuarios.c.escala_id.in_(escala_ids))
        escala_usuarios_result = await db.execute(escala_usuarios_query)
        escala_usuarios_rows = escala_usuarios_result.fetchall()
        
        # Get user data for escala_usuarios
        usuario_ids = [row.usuario_id for row in escala_usuarios_rows]
        if usuario_ids:
            usuarios_query = select(Usuario).where(Usuario.id.in_(usuario_ids))
            usuarios_result = await db.execute(usuarios_query)
            usuarios_dict = {u.id: u for u in usuarios_result.scalars().all()}
            
            # Group escala_usuarios by escala_id
            for row in escala_usuarios_rows:
                if row.escala_id not in escala_usuarios_data:
                    escala_usuarios_data[row.escala_id] = []
                usuario = usuarios_dict.get(row.usuario_id)
                escala_usuarios_data[row.escala_id].append({
                    "id": row.id,
                    "usuario_id": row.usuario_id,
                    "setor": row.setor,
                    "status": row.status,
                    "usuario": {
                        "id": usuario.id,
                        "nome": usuario.nome,
                        "email": usuario.email,
                        "perfil": usuario.perfil.value
                    } if usuario else None
                })
    
    # Group by date
    calendar_data = {}
    for escala in escalas:
        date_key = escala.data_inicio
        if date_key not in calendar_data:
            calendar_data[date_key] = []
        
        # Create escala response with usuarios_atribuidos
        escala_dict = {
            "id": escala.id,
            "data_inicio": escala.data_inicio,
            "data_fim": escala.data_fim,
            "hora_inicio": escala.hora_inicio,
            "hora_fim": escala.hora_fim,
            "estabelecimento_id": escala.estabelecimento_id,
            "status": escala.status,
            "observacoes": escala.observacoes,
            "created_at": escala.created_at,
            "updated_at": escala.updated_at,
            "estabelecimento": {
                "id": escala.estabelecimento.id,
                "nome": escala.estabelecimento.nome,
                "endereco": escala.estabelecimento.endereco
            } if escala.estabelecimento else None,
            "usuarios_atribuidos": escala_usuarios_data.get(escala.id, [])
        }
        calendar_data[date_key].append(escala_dict)
    
    # Create calendar view
    calendar_view = []
    current_date = start_date
    while current_date <= end_date:
        calendar_view.append(EscalaCalendarView(
            data=current_date,
            escalas=calendar_data.get(current_date, [])
        ))
        current_date += timedelta(days=1)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_CALENDAR",
        details={"start_date": str(start_date), "end_date": str(end_date)},
        db=db
    )
    
    return calendar_view


@router.get("/{escala_id}", response_model=EscalaResponse)
async def get_escala(
    escala_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get schedule by ID
    """
    # Get schedule
    result = await db.execute(
        select(Escala)
        .options(selectinload(Escala.estabelecimento))
        .options(selectinload(Escala.supervisores))
        .where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Get usuarios_atribuidos for this scale
    escala_usuarios_query = select(escala_usuarios).where(escala_usuarios.c.escala_id == escala_id)
    escala_usuarios_result = await db.execute(escala_usuarios_query)
    escala_usuarios_rows = escala_usuarios_result.fetchall()
    
    usuarios_atribuidos = []
    if escala_usuarios_rows:
        usuario_ids = [row.usuario_id for row in escala_usuarios_rows]
        usuarios_query = select(Usuario).where(Usuario.id.in_(usuario_ids))
        usuarios_result = await db.execute(usuarios_query)
        usuarios_dict = {u.id: u for u in usuarios_result.scalars().all()}
        
        for row in escala_usuarios_rows:
            usuario = usuarios_dict.get(row.usuario_id)
            usuarios_atribuidos.append({
                "id": row.id,
                "usuario_id": row.usuario_id,
                "setor": row.setor,
                "status": row.status,
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "perfil": usuario.perfil.value
                } if usuario else None
            })
    
    # Check permissions - sócios can only view schedules they are assigned to
    if (current_user.perfil == PerfilEnum.SOCIO and 
        not any(u["usuario_id"] == current_user.id for u in usuarios_atribuidos)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this schedule"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_ESCALA",
        resource="Escala",
        resource_id=escala_id,
        db=db
    )
    
    # Create response with usuarios_atribuidos
    escala_dict = {
        "id": escala.id,
        "data_inicio": escala.data_inicio,
        "data_fim": escala.data_fim,
        "hora_inicio": escala.hora_inicio,
        "hora_fim": escala.hora_fim,
        "estabelecimento_id": escala.estabelecimento_id,
        "status": escala.status,
        "observacoes": escala.observacoes,
        "created_at": escala.created_at,
        "updated_at": escala.updated_at,
        "estabelecimento": {
            "id": escala.estabelecimento.id,
            "nome": escala.estabelecimento.nome,
            "endereco": escala.estabelecimento.endereco
        } if escala.estabelecimento else None,
        "usuarios_atribuidos": usuarios_atribuidos
    }
    
    return escala_dict


@router.post("/", response_model=EscalaResponse)
async def create_escala(
    escala_data: EscalaCreate,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new schedule
    Only supervisors and admins can create schedules
    """
    # Validate establishment exists
    result = await db.execute(
        select(Estabelecimento).where(Estabelecimento.id == escala_data.estabelecimento_id)
    )
    estabelecimento = result.scalar_one_or_none()
    
    if not estabelecimento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Establishment not found"
        )
    
    # Create schedule (only basic data)
    nova_escala = Escala(
        data_inicio=escala_data.data_inicio,
        data_fim=escala_data.data_fim,
        hora_inicio=escala_data.hora_inicio,
        hora_fim=escala_data.hora_fim,
        estabelecimento_id=escala_data.estabelecimento_id,
        observacoes=escala_data.observacoes,
        status=StatusEscalaEnum.PENDENTE
    )
    
    db.add(nova_escala)
    await db.commit()
    await db.refresh(nova_escala)
    
    # Load establishment relationship
    await db.refresh(nova_escala, ['estabelecimento'])
    
    # Adicionar supervisores se fornecidos
    if escala_data.supervisores_ids:
        # Verificar se todos os supervisores existem e são supervisores
        for supervisor_id in escala_data.supervisores_ids:
            result = await db.execute(
                select(Usuario).where(
                    Usuario.id == supervisor_id,
                    Usuario.perfil.in_([PerfilEnum.SUPERVISOR, PerfilEnum.ADMINISTRADOR])
                )
            )
            supervisor = result.scalar_one_or_none()
            
            if not supervisor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Usuário {supervisor_id} não é um supervisor válido"
                )
        
        # Adicionar supervisores à escala
        from app.core.models import escala_supervisores
        for supervisor_id in escala_data.supervisores_ids:
            insert_stmt = escala_supervisores.insert().values(
                escala_id=nova_escala.id,
                usuario_id=supervisor_id
            )
            await db.execute(insert_stmt)
        
        await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="CREATE_ESCALA",
        resource="Escala",
        resource_id=nova_escala.id,
        details=escala_data.dict(),
        db=db
    )
    
    # Get supervisores if any
    supervisores = []
    if escala_data.supervisores_ids:
        result = await db.execute(
            select(Usuario).where(Usuario.id.in_(escala_data.supervisores_ids))
        )
        supervisores_objs = result.scalars().all()
        supervisores = [
            {
                "id": s.id,
                "nome": s.nome,
                "email": s.email,
                "perfil": s.perfil.value
            }
            for s in supervisores_objs
        ]
    
    # Create response with empty usuarios_atribuidos
    escala_dict = {
        "id": nova_escala.id,
        "data_inicio": nova_escala.data_inicio,
        "data_fim": nova_escala.data_fim,
        "hora_inicio": nova_escala.hora_inicio,
        "hora_fim": nova_escala.hora_fim,
        "estabelecimento_id": nova_escala.estabelecimento_id,
        "status": nova_escala.status,
        "observacoes": nova_escala.observacoes,
        "created_at": nova_escala.created_at,
        "updated_at": nova_escala.updated_at,
        "estabelecimento": {
            "id": nova_escala.estabelecimento.id,
            "nome": nova_escala.estabelecimento.nome,
            "endereco": nova_escala.estabelecimento.endereco
        } if nova_escala.estabelecimento else None,
        "usuarios_atribuidos": [],
        "supervisores": supervisores
    }
    
    return escala_dict


@router.post("/bulk", response_model=List[EscalaResponse])
async def create_bulk_escalas(
    bulk_data: EscalaBulkCreate,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create multiple schedules at once
    Only supervisors and admins can create schedules
    """
    created_escalas = []
    errors = []
    
    for i, escala_data in enumerate(bulk_data.escalas):
        try:
            # Validate establishment exists
            result = await db.execute(
                select(Estabelecimento).where(Estabelecimento.id == escala_data.estabelecimento_id)
            )
            estabelecimento = result.scalar_one_or_none()
            
            if not estabelecimento:
                errors.append(f"Schedule {i+1}: Establishment not found")
                continue
            
            # Create schedule (only basic data)
            nova_escala = Escala(
                data_inicio=escala_data.data_inicio,
                data_fim=escala_data.data_fim,
                hora_inicio=escala_data.hora_inicio,
                hora_fim=escala_data.hora_fim,
                estabelecimento_id=escala_data.estabelecimento_id,
                observacoes=escala_data.observacoes,
                status=StatusEscalaEnum.PENDENTE
            )
            
            db.add(nova_escala)
            created_escalas.append(nova_escala)
            
        except Exception as e:
            errors.append(f"Schedule {i+1}: {str(e)}")
    
    if errors:
        # Rollback and return errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Some schedules could not be created",
                "errors": errors
            }
        )
    
    await db.commit()
    
    # Refresh and load relationships
    for escala in created_escalas:
        await db.refresh(escala, ['estabelecimento'])
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="CREATE_BULK_ESCALAS",
        details={"count": len(created_escalas)},
        db=db
    )
    
    # Create responses with empty usuarios_atribuidos
    responses = []
    for escala in created_escalas:
        escala_dict = {
            "id": escala.id,
            "data_inicio": escala.data_inicio,
            "data_fim": escala.data_fim,
            "hora_inicio": escala.hora_inicio,
            "hora_fim": escala.hora_fim,
            "estabelecimento_id": escala.estabelecimento_id,
            "status": escala.status,
            "observacoes": escala.observacoes,
            "created_at": escala.created_at,
            "updated_at": escala.updated_at,
            "estabelecimento": {
                "id": escala.estabelecimento.id,
                "nome": escala.estabelecimento.nome,
                "endereco": escala.estabelecimento.endereco
            } if escala.estabelecimento else None,
            "usuarios_atribuidos": []
        }
        responses.append(escala_dict)
    
    return responses


@router.put("/{escala_id}", response_model=EscalaResponse)
async def update_escala(
    escala_id: int,
    escala_data: EscalaUpdate,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update schedule
    Only supervisors and admins can update schedules
    """
    # Get schedule
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Check if there's already a check-in for this schedule
    checkin_result = await db.execute(
        select(Checkin).where(Checkin.escala_id == escala_id)
    )
    if checkin_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify schedule that already has a check-in"
        )
    
    # Validate establishment if changing
    if escala_data.estabelecimento_id and escala_data.estabelecimento_id != escala.estabelecimento_id:
        result = await db.execute(
            select(Estabelecimento).where(Estabelecimento.id == escala_data.estabelecimento_id)
        )
        estabelecimento = result.scalar_one_or_none()
        
        if not estabelecimento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Establishment not found"
            )
        
        conflict_result = await db.execute(conflict_query)
        if conflict_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Schedule conflicts with existing schedule for this user"
            )
    
    # Update fields
    update_data = escala_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(escala, field):
            setattr(escala, field, value)
    
    await db.commit()
    await db.refresh(escala, ['estabelecimento'])
    
    # Get usuarios_atribuidos for this scale
    escala_usuarios_query = select(escala_usuarios).where(escala_usuarios.c.escala_id == escala_id)
    escala_usuarios_result = await db.execute(escala_usuarios_query)
    escala_usuarios_rows = escala_usuarios_result.fetchall()
    
    usuarios_atribuidos = []
    if escala_usuarios_rows:
        usuario_ids = [row.usuario_id for row in escala_usuarios_rows]
        usuarios_query = select(Usuario).where(Usuario.id.in_(usuario_ids))
        usuarios_result = await db.execute(usuarios_query)
        usuarios_dict = {u.id: u for u in usuarios_result.scalars().all()}
        
        for row in escala_usuarios_rows:
            usuario = usuarios_dict.get(row.usuario_id)
            usuarios_atribuidos.append({
                "id": row.id,
                "usuario_id": row.usuario_id,
                "setor": row.setor,
                "status": row.status,
                "usuario": {
                    "id": usuario.id,
                    "nome": usuario.nome,
                    "email": usuario.email,
                    "perfil": usuario.perfil.value
                } if usuario else None
            })
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="UPDATE_ESCALA",
        resource="Escala",
        resource_id=escala_id,
        details=update_data,
        db=db
    )
    
    # Create response with usuarios_atribuidos
    escala_dict = {
        "id": escala.id,
        "data_inicio": escala.data_inicio,
        "data_fim": escala.data_fim,
        "hora_inicio": escala.hora_inicio,
        "hora_fim": escala.hora_fim,
        "estabelecimento_id": escala.estabelecimento_id,
        "status": escala.status,
        "observacoes": escala.observacoes,
        "created_at": escala.created_at,
        "updated_at": escala.updated_at,
        "estabelecimento": {
            "id": escala.estabelecimento.id,
            "nome": escala.estabelecimento.nome,
            "endereco": escala.estabelecimento.endereco
        } if escala.estabelecimento else None,
        "usuarios_atribuidos": usuarios_atribuidos
    }
    
    return escala_dict


@router.delete("/{escala_id}")
async def delete_escala(
    escala_id: int,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete schedule
    Only supervisors and admins can delete schedules
    """
    # Get schedule
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Check if there's already a check-in for this schedule
    from app.core.models import Checkin
    checkin_result = await db.execute(
        select(Checkin).where(Checkin.escala_id == escala_id)
    )
    if checkin_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete schedule that already has a check-in"
        )
    
    # Delete related records first (escala_usuarios, escala_supervisores)
    from app.core.models import escala_usuarios, escala_supervisores
    
    # Delete escala_usuarios relationships
    await db.execute(
        escala_usuarios.delete().where(escala_usuarios.c.escala_id == escala_id)
    )
    
    # Delete escala_supervisores relationships
    await db.execute(
        escala_supervisores.delete().where(escala_supervisores.c.escala_id == escala_id)
    )
    
    # Delete the schedule itself
    await db.delete(escala)
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="DELETE_ESCALA",
        resource="Escala",
        resource_id=escala_id,
        db=db
    )
    
    return {"message": "Schedule deleted successfully"}


@router.post("/{escala_id}/atribuir-usuario")
async def atribuir_usuario_escala(
    escala_id: int,
    atribuicao_data: dict,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Atribuir usuário a uma escala específica
    """
    # Get schedule
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Get user
    usuario_id = atribuicao_data.get('usuario_id')
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do usuário é obrigatório"
        )
    
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    if usuario.status.value != "Ativo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível atribuir escala a usuário inativo"
        )
    
    # Check if user is already assigned to this schedule
    if escala.usuario_id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já está atribuído a esta escala"
        )
    
    # Check for conflicts
    conflict_query = select(Escala).where(
        and_(
            Escala.id != escala_id,
            Escala.usuario_id == usuario_id,
            Escala.data_inicio == escala.data_inicio,
            or_(
                and_(escala.hora_inicio >= Escala.hora_inicio, escala.hora_inicio < Escala.hora_fim),
                and_(escala.hora_fim > Escala.hora_inicio, escala.hora_fim <= Escala.hora_fim),
                and_(escala.hora_inicio <= Escala.hora_inicio, escala.hora_fim >= Escala.hora_fim)
            )
        )
    )
    
    conflict_result = await db.execute(conflict_query)
    if conflict_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já possui escala conflitante neste horário"
        )
    
    # Update schedule with new user
    escala.usuario_id = usuario_id
    escala.setor = atribuicao_data.get('setor', usuario.setor or 'Geral')
    
    await db.commit()
    await db.refresh(escala, ['usuario'])
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="ATRIBUIR_USUARIO_ESCALA",
        resource="Escala",
        resource_id=escala_id,
        details={
            "usuario_id": usuario_id,
            "usuario_nome": usuario.nome,
            "setor": escala.setor
        },
        db=db
    )
    
    return {
        "message": f"Usuário {usuario.nome} atribuído à escala com sucesso",
        "escala": EscalaResponse.from_orm(escala)
    }


@router.get("/{escala_id}/usuarios", response_model=List[dict])
async def get_usuarios_escala(
    escala_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter usuários atribuídos a uma escala específica
    """
    # Get schedule
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Get assigned user
    if escala.usuario_id:
        result = await db.execute(
            select(Usuario).where(Usuario.id == escala.usuario_id)
        )
        usuario = result.scalar_one_or_none()
        
        if usuario:
            return [{
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "setor": escala.setor or usuario.setor or "Geral",
                "perfil": usuario.perfil.value
            }]
    
    return []


@router.get("/stats/summary", response_model=EscalaStats)
async def get_escala_stats(
    request: Request,
    start_date: date = Query(...),
    end_date: date = Query(...),
    usuario_id: Optional[int] = Query(None),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get schedule statistics for a date range
    Only supervisors and admins can view stats
    """
    # Build conditions
    conditions = [
        Escala.data_inicio >= start_date,
        Escala.data_inicio <= end_date
    ]
    
    if usuario_id:
        conditions.append(Escala.usuario_id == usuario_id)
    
    # Get stats
    stats_query = select(
        func.count(Escala.id).label('total'),
        func.count(func.nullif(Escala.status == StatusEscalaEnum.PENDENTE, False)).label('pendentes'),
        func.count(func.nullif(Escala.status == StatusEscalaEnum.CONFIRMADO, False)).label('confirmadas'),
        func.count(func.nullif(Escala.status == StatusEscalaEnum.AUSENTE, False)).label('ausentes')
    ).where(and_(*conditions))
    
    result = await db.execute(stats_query)
    stats = result.first()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_ESCALA_STATS",
        details={"start_date": str(start_date), "end_date": str(end_date)},
        db=db
    )
    
    total = stats.total or 0
    confirmadas = stats.confirmadas or 0
    percentual_confirmadas = (confirmadas / total * 100) if total > 0 else 0.0
    
    return EscalaStats(
        total_escalas=total,
        pendentes=stats.pendentes or 0,
        confirmadas=confirmadas,
        ausentes=stats.ausentes or 0,
        percentual_confirmadas=percentual_confirmadas,
        periodo_inicio=start_date,
        periodo_fim=end_date
    ) 


# ==========================================
# NOVOS ENDPOINTS PARA MÚLTIPLOS USUÁRIOS
# ==========================================

@router.post("/{escala_id}/usuarios")
async def adicionar_usuario_escala(
    escala_id: int,
    data: dict,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Adicionar usuário à escala com setor específico
    """
    # Verificar se escala existe
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Validar dados
    usuario_id = data.get('usuario_id')
    setor_id = data.get('setor_id')
    
    if not usuario_id or not setor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="usuario_id e setor_id são obrigatórios"
        )
    
    # Verificar se setor existe na tabela de setores
    from app.core.models import Setor
    result = await db.execute(
        select(Setor).where(Setor.id == setor_id, Setor.ativo == True)
    )
    setor_obj = result.scalar_one_or_none()
    
    if not setor_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setor com ID {setor_id} não encontrado ou inativo."
        )
    
    # Verificar se usuário existe
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar se usuário já está na escala
    result = await db.execute(
        select(escala_usuarios).where(
            and_(
                escala_usuarios.c.escala_id == escala_id,
                escala_usuarios.c.usuario_id == usuario_id
            )
        )
    )
    existing = result.first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já está atribuído a esta escala"
        )
    
    # Adicionar usuário à escala
    insert_stmt = escala_usuarios.insert().values(
        escala_id=escala_id,
        usuario_id=usuario_id,
        setor_id=setor_id
    )
    await db.execute(insert_stmt)
    await db.commit()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="ADD_USER_TO_SCHEDULE",
        resource="Escala",
        resource_id=escala_id,
        details={
            "usuario_id": usuario_id,
            "usuario_nome": usuario.nome,
            "setor": setor
        },
        db=db
    )
    
    return {
        "message": f"Usuário {usuario.nome} adicionado à escala",
        "usuario_id": usuario_id,
        "setor": setor_upper
    }


@router.delete("/{escala_id}/usuarios/{usuario_id}")
async def remover_usuario_escala(
    escala_id: int,
    usuario_id: int,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Remover usuário da escala
    """
    # Verificar se escala existe
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Verificar se usuário está na escala
    result = await db.execute(
        select(escala_usuarios).where(
            and_(
                escala_usuarios.c.escala_id == escala_id,
                escala_usuarios.c.usuario_id == usuario_id
            )
        )
    )
    existing = result.first()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não está atribuído a esta escala"
        )
    
    # Remover usuário da escala
    delete_stmt = escala_usuarios.delete().where(
        and_(
            escala_usuarios.c.escala_id == escala_id,
            escala_usuarios.c.usuario_id == usuario_id
        )
    )
    await db.execute(delete_stmt)
    await db.commit()
    
    # Get user name for log
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="REMOVE_USER_FROM_SCHEDULE",
        resource="Escala",
        resource_id=escala_id,
        details={
            "usuario_id": usuario_id,
            "usuario_nome": usuario.nome if usuario else "Usuário não encontrado"
        },
        db=db
    )
    
    return {"message": "Usuário removido da escala com sucesso"}


@router.get("/{escala_id}/usuarios-multiplos", response_model=List[dict])
async def get_usuarios_multiplos_escala(
    escala_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obter todos os usuários atribuídos a uma escala (incluindo múltiplos)
    """
    # Verificar se escala existe
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Buscar usuários múltiplos
    query = select(
        Usuario.id,
        Usuario.nome,
        Usuario.email,
        Usuario.perfil,
        escala_usuarios.c.setor
    ).join(
        escala_usuarios, Usuario.id == escala_usuarios.c.usuario_id
    ).where(
        escala_usuarios.c.escala_id == escala_id
    )
    
    result = await db.execute(query)
    usuarios_multiplos = result.all()
    
    # Se não há usuários múltiplos, retornar usuário principal da escala
    if not usuarios_multiplos and escala.usuario_id:
        result = await db.execute(
            select(Usuario).where(Usuario.id == escala.usuario_id)
        )
        usuario_principal = result.scalar_one_or_none()
        
        if usuario_principal:
            return [{
                "id": usuario_principal.id,
                "nome": usuario_principal.nome,
                "email": usuario_principal.email,
                "perfil": usuario_principal.perfil.value,
                "setor": escala.setor or "Não definido"
            }]
    
    # Retornar usuários múltiplos
    return [
        {
            "id": user.id,
            "nome": user.nome,
            "email": user.email,
            "perfil": user.perfil.value,
            "setor": user.setor
        }
        for user in usuarios_multiplos
    ]


@router.put("/{escala_id}/usuarios/{usuario_id}")
async def atualizar_setor_usuario_escala(
    escala_id: int,
    usuario_id: int,
    data: dict,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualizar setor do usuário na escala
    """
    novo_setor_id = data.get('setor_id')
    if not novo_setor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="setor_id é obrigatório"
        )
    
    # Verificar se setor existe na tabela de setores
    from app.core.models import Setor
    result = await db.execute(
        select(Setor).where(Setor.id == novo_setor_id, Setor.ativo == True)
    )
    setor_obj = result.scalar_one_or_none()
    
    if not setor_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setor com ID {novo_setor_id} não encontrado ou inativo."
        )
    
    # Verificar se escala existe
    result = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Verificar se usuário está na escala
    result = await db.execute(
        select(escala_usuarios).where(
            and_(
                escala_usuarios.c.escala_id == escala_id,
                escala_usuarios.c.usuario_id == usuario_id
            )
        )
    )
    existing = result.first()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não está atribuído a esta escala"
        )
    
    # Atualizar setor
    update_stmt = escala_usuarios.update().where(
        and_(
            escala_usuarios.c.escala_id == escala_id,
            escala_usuarios.c.usuario_id == usuario_id
        )
    ).values(setor_id=novo_setor_id)
    
    await db.execute(update_stmt)
    await db.commit()
    
    # Get user name for log
    result = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = result.scalar_one_or_none()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="UPDATE_USER_SECTOR_IN_SCHEDULE",
        resource="Escala",
        resource_id=escala_id,
        details={
            "usuario_id": usuario_id,
            "usuario_nome": usuario.nome if usuario else "Usuário não encontrado",
            "novo_setor_id": novo_setor_id,
            "setor_anterior_id": existing.setor_id
        },
        db=db
    )
    
    return {
        "message": "Setor atualizado com sucesso",
        "usuario_id": usuario_id,
        "novo_setor_id": novo_setor_id
    }

 