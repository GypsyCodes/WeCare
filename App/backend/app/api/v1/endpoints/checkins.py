"""
Check-in management endpoints
"""
from typing import List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import math

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import (
    Checkin, Escala, Usuario, StatusCheckinEnum, 
    StatusEscalaEnum, PerfilEnum
)
from app.core.deps import get_current_user, require_supervisor, PermissionChecker, log_action
from app.core.config import settings
from app.schemas.checkin import (
    CheckinResponse, CheckinCreate, CheckinUpdate, CheckinListResponse,
    CheckinFilter, CheckinStats, CheckinValidation, LocationValidation
)

router = APIRouter()


def calculate_distance(lat1: Decimal, lon1: Decimal, lat2: Decimal, lon2: Decimal) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula
    Returns distance in meters
    """
    # Convert to float for calculation
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in meters
    r = 6371000
    
    return c * r


@router.get("/", response_model=CheckinListResponse)
async def list_checkins(
    request: Request,
    filter_params: CheckinFilter = Depends(),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List check-ins with pagination and filters
    Sócios can only see their own check-ins
    """
    # Build base query
    query = select(Checkin).options(
        selectinload(Checkin.usuario),
        selectinload(Checkin.escala)
    )
    
    # Apply user restrictions
    conditions = []
    if current_user.perfil == PerfilEnum.SOCIO:
        conditions.append(Checkin.usuario_id == current_user.id)
    elif filter_params.usuario_id:
        conditions.append(Checkin.usuario_id == filter_params.usuario_id)
    
    # Apply filters
    if filter_params.escala_id:
        conditions.append(Checkin.escala_id == filter_params.escala_id)
    
    if filter_params.data_inicio:
        conditions.append(Checkin.data_hora >= filter_params.data_inicio)
    
    if filter_params.data_fim:
        conditions.append(Checkin.data_hora <= filter_params.data_fim)
    
    if filter_params.status:
        conditions.append(Checkin.status == filter_params.status)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count total
    count_query = select(func.count(Checkin.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (filter_params.page - 1) * filter_params.per_page
    query = query.offset(offset).limit(filter_params.per_page)
    query = query.order_by(Checkin.data_hora.desc())
    
    # Execute query
    result = await db.execute(query)
    checkins = result.scalars().all()
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="LIST_CHECKINS",
        details={"filters": filter_params.dict()},
        db=db
    )
    
    # Calculate pagination
    pages = (total + filter_params.per_page - 1) // filter_params.per_page
    
    return CheckinListResponse(
        checkins=[CheckinResponse.from_orm(checkin) for checkin in checkins],
        total=total,
        page=filter_params.page,
        per_page=filter_params.per_page,
        pages=pages
    )


@router.get("/{checkin_id}", response_model=CheckinResponse)
async def get_checkin(
    checkin_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get check-in by ID
    """
    # Get check-in
    result = await db.execute(
        select(Checkin)
        .options(selectinload(Checkin.usuario), selectinload(Checkin.escala))
        .where(Checkin.id == checkin_id)
    )
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    
    # Check permissions - sócios can only view their own check-ins
    if (current_user.perfil == PerfilEnum.SOCIO and 
        checkin.usuario_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this check-in"
        )
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_CHECKIN",
        resource="Checkin",
        resource_id=checkin_id,
        db=db
    )
    
    return CheckinResponse.from_orm(checkin)


@router.post("/validate", response_model=CheckinValidation)
async def validate_checkin_location(
    validation_data: LocationValidation,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate if check-in can be performed at given location
    """
    # For this example, we'll use a simple validation
    # In production, you would have predefined work locations in the database
    
    # Example work locations (in production, these would be in the database)
    WORK_LOCATIONS = [
        {"name": "Hospital Principal", "lat": Decimal("-23.550520"), "lon": Decimal("-46.633308")},
        {"name": "Clínica Norte", "lat": Decimal("-23.545678"), "lon": Decimal("-46.628901")},
        {"name": "UBS Centro", "lat": Decimal("-23.552341"), "lon": Decimal("-46.635789")},
    ]
    
    # Find closest work location
    min_distance = float('inf')
    closest_location = None
    
    for location in WORK_LOCATIONS:
        distance = calculate_distance(
            validation_data.latitude, validation_data.longitude,
            location["lat"], location["lon"]
        )
        
        if distance < min_distance:
            min_distance = distance
            closest_location = location
    
    # Check if within tolerance
    is_valid = min_distance <= settings.GPS_TOLERANCE_METERS
    
    # Log validation attempt
    await log_action(
        request=request,
        current_user=current_user,
        action="VALIDATE_LOCATION",
        details={
            "latitude": str(validation_data.latitude),
            "longitude": str(validation_data.longitude),
            "distance": min_distance,
            "valid": is_valid
        },
        db=db
    )
    
    if is_valid:
        message = f"Location validated. You are {min_distance:.0f}m from {closest_location['name']}"
    else:
        message = f"Location not valid. You are {min_distance:.0f}m from the nearest work location. Maximum allowed distance is {settings.GPS_TOLERANCE_METERS}m"
    
    return CheckinValidation(
        escala_id=0,  # This would be provided in the actual check-in request
        gps_lat=validation_data.latitude,
        gps_long=validation_data.longitude,
        valid=is_valid,
        message=message,
        distance_from_location=min_distance
    )


@router.post("/", response_model=CheckinResponse)
async def create_checkin(
    checkin_data: CheckinCreate,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform check-in for a schedule
    """
    # Get schedule
    result = await db.execute(
        select(Escala)
        .options(selectinload(Escala.usuario))
        .where(Escala.id == checkin_data.escala_id)
    )
    escala = result.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    # Check permissions
    if not PermissionChecker.can_perform_checkin(current_user, escala.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to perform this check-in"
        )
    
    # Check if check-in already exists
    existing_checkin = await db.execute(
        select(Checkin).where(Checkin.escala_id == checkin_data.escala_id)
    )
    if existing_checkin.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in already exists for this schedule"
        )
    
    # Validate timing - check-in allowed 15 minutes before schedule starts
    now = datetime.now()
    schedule_datetime = datetime.combine(escala.data_inicio, escala.hora_inicio)
    allowed_checkin_time = schedule_datetime - timedelta(minutes=settings.CHECKIN_WINDOW_MINUTES)
    
    if now < allowed_checkin_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Check-in not allowed yet. You can check-in starting {settings.CHECKIN_WINDOW_MINUTES} minutes before your shift"
        )
    
    # Check if too late (more than 1 hour after start)
    late_limit = schedule_datetime + timedelta(hours=1)
    if now > late_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check-in period has expired. Contact your supervisor"
        )
    
    # Validate location
    validation = await validate_checkin_location(
        LocationValidation(
            latitude=checkin_data.gps_lat,
            longitude=checkin_data.gps_long
        ),
        request,
        current_user,
        db
    )
    
    # Allow check-in even if location is not perfect, but mark status accordingly
    checkin_status = StatusCheckinEnum.REALIZADO
    if not validation.valid:
        checkin_status = StatusCheckinEnum.FORA_DE_LOCAL
    
    # Create check-in
    novo_checkin = Checkin(
        usuario_id=current_user.id,
        escala_id=checkin_data.escala_id,
        data_hora=now,
        gps_lat=checkin_data.gps_lat,
        gps_long=checkin_data.gps_long,
        endereco=checkin_data.endereco,
        observacoes=checkin_data.observacoes,
        status=checkin_status
    )
    
    # Update schedule status
    escala.status = StatusEscalaEnum.CONFIRMADO
    
    db.add(novo_checkin)
    await db.commit()
    await db.refresh(novo_checkin, ['usuario', 'escala'])
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="CREATE_CHECKIN",
        resource="Checkin",
        resource_id=novo_checkin.id,
        details={
            "escala_id": checkin_data.escala_id,
            "status": checkin_status.value,
            "location_valid": validation.valid
        },
        db=db
    )
    
    return CheckinResponse.from_orm(novo_checkin)


@router.put("/{checkin_id}", response_model=CheckinResponse)
async def update_checkin(
    checkin_id: int,
    checkin_data: CheckinUpdate,
    request: Request,
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update check-in (admin/supervisor only)
    Only supervisors and admins can update check-ins
    """
    # Get check-in
    result = await db.execute(
        select(Checkin).where(Checkin.id == checkin_id)
    )
    checkin = result.scalar_one_or_none()
    
    if not checkin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Check-in not found"
        )
    
    # Update fields
    update_data = checkin_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(checkin, field):
            setattr(checkin, field, value)
    
    await db.commit()
    await db.refresh(checkin, ['usuario', 'escala'])
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="UPDATE_CHECKIN",
        resource="Checkin",
        resource_id=checkin_id,
        details=update_data,
        db=db
    )
    
    return CheckinResponse.from_orm(checkin)


@router.get("/stats/summary", response_model=CheckinStats)
async def get_checkin_stats(
    request: Request,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    usuario_id: Optional[int] = Query(None),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get check-in statistics for a date range
    Only supervisors and admins can view stats
    """
    # Build conditions
    conditions = [
        Checkin.data_hora >= start_date,
        Checkin.data_hora <= end_date
    ]
    
    if usuario_id:
        conditions.append(Checkin.usuario_id == usuario_id)
    
    # Get stats
    stats_query = select(
        func.count(Checkin.id).label('total'),
        func.count(func.nullif(Checkin.status == StatusCheckinEnum.REALIZADO, False)).label('realizados'),
        func.count(func.nullif(Checkin.status == StatusCheckinEnum.AUSENTE, False)).label('ausentes'),
        func.count(func.nullif(Checkin.status == StatusCheckinEnum.FORA_DE_LOCAL, False)).label('fora_local')
    ).where(and_(*conditions))
    
    result = await db.execute(stats_query)
    stats = result.first()
    
    # Calculate attendance rate
    total = stats.total or 0
    realizados = stats.realizados or 0
    taxa_presenca = (realizados / total * 100) if total > 0 else 0
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_CHECKIN_STATS",
        details={"start_date": str(start_date), "end_date": str(end_date)},
        db=db
    )
    
    return CheckinStats(
        total_checkins=total,
        realizados=realizados,
        ausentes=stats.ausentes or 0,
        fora_de_local=stats.fora_local or 0,
        taxa_presenca=round(taxa_presenca, 2),
        periodo_inicio=start_date,
        periodo_fim=end_date
    )


@router.get("/my-pending")
async def get_my_pending_checkins(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending check-ins for current user (schedules without check-in)
    """
    now = datetime.now()
    today = now.date()
    
    # Get schedules without check-ins for today
    subquery = select(Checkin.escala_id).where(Checkin.escala_id == Escala.id)
    
    query = select(Escala).options(selectinload(Escala.usuario)).where(
        and_(
            Escala.usuario_id == current_user.id,
            Escala.data_inicio == today,
            Escala.status == StatusEscalaEnum.PENDENTE,
            ~exists(subquery)  # No check-in exists
        )
    ).order_by(Escala.hora_inicio.asc())
    
    result = await db.execute(query)
    pending_schedules = result.scalars().all()
    
    # Check which ones are available for check-in
    available_checkins = []
    for escala in pending_schedules:
        schedule_datetime = datetime.combine(escala.data_inicio, escala.hora_inicio)
        allowed_time = schedule_datetime - timedelta(minutes=settings.CHECKIN_WINDOW_MINUTES)
        late_limit = schedule_datetime + timedelta(hours=1)
        
        status = "pending"  # Not yet time
        if now >= allowed_time:
            if now <= late_limit:
                status = "available"  # Can check-in now
            else:
                status = "expired"  # Too late
        
        available_checkins.append({
            "escala_id": escala.id,
            "data": escala.data_inicio,
            "hora_inicio": escala.hora_inicio,
            "hora_fim": escala.hora_fim,
            "status": status,
            "can_checkin": status == "available"
        })
    
    return {
        "pending_checkins": available_checkins,
        "total": len(available_checkins)
    } 