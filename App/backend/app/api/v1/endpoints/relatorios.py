"""
Report generation endpoints
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, between, text
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import (
    Usuario, Escala, Checkin, Log, Documento,
    StatusEscalaEnum, StatusCheckinEnum, PerfilEnum, StatusUsuarioEnum, Estabelecimento
)
from app.core.deps import require_supervisor, get_current_user, log_action
from app.schemas.relatorio import (
    RelatorioCheckinResponse, RelatorioEscalaResponse, RelatorioHorasResponse,
    RelatorioFilter, DashboardStats, RelatorioAuditoria
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    request: Request,
    periodo_dias: int = Query(30, ge=1, le=365),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard statistics overview
    Only supervisors and admins can view dashboard
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=periodo_dias)
    
    # Get user stats
    users_query = select(
        func.count(Usuario.id).label('total_usuarios'),
        func.count(func.nullif(Usuario.status.in_(['Ativo']), False)).label('usuarios_ativos'),
        func.count(func.nullif(Usuario.perfil == PerfilEnum.SOCIO, False)).label('socios'),
        func.count(func.nullif(Usuario.perfil == PerfilEnum.SUPERVISOR, False)).label('supervisores')
    )
    users_result = await db.execute(users_query)
    users_stats = users_result.first()
    
    # Get schedule stats for period
    schedules_query = select(
        func.count(Escala.id).label('total_escalas'),
        func.count(func.nullif(Escala.status == StatusEscalaEnum.CONFIRMADO, False)).label('confirmadas'),
        func.count(func.nullif(Escala.status == StatusEscalaEnum.PENDENTE, False)).label('pendentes'),
        func.count(func.nullif(Escala.status == StatusEscalaEnum.AUSENTE, False)).label('ausentes')
    ).where(
        and_(
            Escala.data_inicio >= start_date.date(),
            Escala.data_inicio <= end_date.date()
        )
    )
    schedules_result = await db.execute(schedules_query)
    schedules_stats = schedules_result.first()
    
    # Get check-in stats for period
    checkins_query = select(
        func.count(Checkin.id).label('total_checkins'),
        func.count(func.nullif(Checkin.status == StatusCheckinEnum.REALIZADO, False)).label('realizados'),
        func.count(func.nullif(Checkin.status == StatusCheckinEnum.FORA_DE_LOCAL, False)).label('fora_local'),
        func.count(func.nullif(Checkin.status == StatusCheckinEnum.AUSENTE, False)).label('ausentes')
    ).where(
        and_(
            Checkin.data_hora >= start_date,
            Checkin.data_hora <= end_date
        )
    )
    checkins_result = await db.execute(checkins_query)
    checkins_stats = checkins_result.first()
    
    # Get document stats
    documents_query = select(
        func.count(Documento.id).label('total_documentos'),
        func.count(func.nullif(Documento.processado == True, False)).label('processados'),
        func.count(func.nullif(Documento.processado == False, False)).label('pendentes')
    )
    documents_result = await db.execute(documents_query)
    documents_stats = documents_result.first()
    
    # Calculate attendance rate
    total_schedules = schedules_stats.total_escalas or 0
    confirmed_schedules = schedules_stats.confirmadas or 0
    attendance_rate = (confirmed_schedules / total_schedules * 100) if total_schedules > 0 else 0
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="VIEW_DASHBOARD",
        details={"periodo_dias": periodo_dias},
        db=db
    )
    
    return DashboardStats(
        periodo_inicio=start_date.date(),
        periodo_fim=end_date.date(),
        total_usuarios=users_stats.total_usuarios or 0,
        usuarios_ativos=users_stats.usuarios_ativos or 0,
        total_socios=users_stats.socios or 0,
        total_supervisores=users_stats.supervisores or 0,
        total_escalas=total_schedules,
        escalas_confirmadas=confirmed_schedules,
        escalas_pendentes=schedules_stats.pendentes or 0,
        escalas_ausentes=schedules_stats.ausentes or 0,
        total_checkins=checkins_stats.total_checkins or 0,
        checkins_realizados=checkins_stats.realizados or 0,
        checkins_fora_local=checkins_stats.fora_local or 0,
        checkins_ausentes=checkins_stats.ausentes or 0,
        taxa_presenca=round(attendance_rate, 2),
        total_documentos=documents_stats.total_documentos or 0,
        documentos_processados=documents_stats.processados or 0,
        documentos_pendentes=documents_stats.pendentes or 0
    )


@router.get("/dashboard-stats")
async def get_dashboard_stats_simple(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get simplified dashboard statistics for the main dashboard
    """
    today = date.today()
    
    # Escalas de hoje
    escalas_hoje_query = select(func.count(Escala.id)).where(
        Escala.data_inicio == today
    )
    escalas_hoje_result = await db.execute(escalas_hoje_query)
    escalas_hoje = escalas_hoje_result.scalar() or 0
    
    # Check-ins pendentes (escalas de hoje sem check-in)
    checkins_pendentes_query = select(func.count(Escala.id)).where(
        and_(
            Escala.data_inicio == today,
            Escala.status == StatusEscalaEnum.CONFIRMADO,
            ~Escala.id.in_(
                select(Checkin.escala_id).where(
                    Checkin.data_hora >= datetime.combine(today, datetime.min.time())
                )
            )
        )
    )
    checkins_pendentes_result = await db.execute(checkins_pendentes_query)
    checkins_pendentes = checkins_pendentes_result.scalar() or 0
    
    # Usuários ativos
    usuarios_ativos_query = select(func.count(Usuario.id)).where(
        Usuario.status == StatusUsuarioEnum.ATIVO
    )
    usuarios_ativos_result = await db.execute(usuarios_ativos_query)
    usuarios_ativos = usuarios_ativos_result.scalar() or 0
    
    # Estabelecimentos ativos
    estabelecimentos_query = select(func.count(Estabelecimento.id)).where(
        Estabelecimento.ativo == True
    )
    estabelecimentos_result = await db.execute(estabelecimentos_query)
    estabelecimentos = estabelecimentos_result.scalar() or 0
    
    # Alertas do sistema
    alertas = []
    
    # Alerta para check-ins pendentes
    if checkins_pendentes > 0:
        alertas.append({
            "id": 1,
            "tipo": "warning",
            "mensagem": f"{checkins_pendentes} check-ins pendentes para hoje"
        })
    
    # Alerta para escalas não confirmadas
    escalas_nao_confirmadas_query = select(func.count(Escala.id)).where(
        and_(
            Escala.data_inicio == today,
            Escala.status == StatusEscalaEnum.PENDENTE
        )
    )
    escalas_nao_confirmadas_result = await db.execute(escalas_nao_confirmadas_query)
    escalas_nao_confirmadas = escalas_nao_confirmadas_result.scalar() or 0
    
    if escalas_nao_confirmadas > 0:
        alertas.append({
            "id": 2,
            "tipo": "info",
            "mensagem": f"{escalas_nao_confirmadas} escalas pendentes de confirmação"
        })
    
    return {
        "escalasHoje": escalas_hoje,
        "checkinsPendentes": checkins_pendentes,
        "usuariosAtivos": usuarios_ativos,
        "estabelecimentos": estabelecimentos,
        "alertas": alertas
    }


@router.get("/checkins-semana")
async def get_checkins_semana(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get check-ins data for the last 7 days for chart
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Query para obter check-ins por dia da semana
    checkins_query = select(
        func.date(Checkin.data_hora).label('data'),
        func.count(Checkin.id).label('total')
    ).where(
        and_(
            Checkin.data_hora >= start_date,
            Checkin.data_hora <= end_date,
            Checkin.status == StatusCheckinEnum.REALIZADO
        )
    ).group_by(
        func.date(Checkin.data_hora)
    ).order_by(
        func.date(Checkin.data_hora)
    )
    
    checkins_result = await db.execute(checkins_query)
    checkins_data = checkins_result.fetchall()
    
    # Preparar dados para o gráfico
    labels = []
    data = []
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime('%a')  # Seg, Ter, Qua, etc.
        labels.append(date_str)
        
        # Encontrar dados para esta data
        found = False
        for row in checkins_data:
            if row.data == current_date.date():
                data.append(row.total)
                found = True
                break
        
        if not found:
            data.append(0)
    
    return {
        "labels": labels,
        "data": data
    }


@router.get("/escalas-mes")
async def get_escalas_mes(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get escalas data for the current month for chart
    """
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    
    # Calcular semanas do mês
    weeks = []
    current_date = start_of_month
    week_num = 1
    
    while current_date.month == today.month:
        week_start = current_date
        week_end = min(current_date + timedelta(days=6), date(today.year, today.month + 1, 1) - timedelta(days=1))
        
        # Contar escalas confirmadas nesta semana
        escalas_query = select(func.count(Escala.id)).where(
            and_(
                Escala.data_inicio >= week_start,
                Escala.data_inicio <= week_end,
                Escala.status == StatusEscalaEnum.CONFIRMADO
            )
        )
        escalas_result = await db.execute(escalas_query)
        escalas_count = escalas_result.scalar() or 0
        
        weeks.append({
            "semana": f"Sem {week_num}",
            "total": escalas_count
        })
        
        current_date += timedelta(days=7)
        week_num += 1
    
    return {
        "labels": [week["semana"] for week in weeks],
        "data": [week["total"] for week in weeks]
    }


@router.get("/usuarios-perfil")
async def get_usuarios_perfil(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get users count by profile for chart
    """
    # Contar usuários por perfil
    usuarios_query = select(
        Usuario.perfil,
        func.count(Usuario.id).label('total')
    ).where(
        Usuario.status == StatusUsuarioEnum.ATIVO
    ).group_by(
        Usuario.perfil
    )
    
    usuarios_result = await db.execute(usuarios_query)
    usuarios_data = usuarios_result.fetchall()
    
    # Preparar dados para o gráfico
    labels = []
    data = []
    
    for row in usuarios_data:
        if row.perfil == PerfilEnum.ADMINISTRADOR:
            labels.append("Administradores")
        elif row.perfil == PerfilEnum.SUPERVISOR:
            labels.append("Supervisores")
        elif row.perfil == PerfilEnum.SOCIO:
            labels.append("Sócios")
        else:
            labels.append(str(row.perfil))
        
        data.append(row.total)
    
    return {
        "labels": labels,
        "data": data
    }


@router.get("/checkins", response_model=List[RelatorioCheckinResponse])
async def get_checkin_report(
    request: Request,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    usuario_id: Optional[int] = Query(None),
    status: Optional[StatusCheckinEnum] = Query(None),
    export_pdf: bool = Query(False),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate check-in report with filters
    Only supervisors and admins can generate reports
    """
    # Validate date range
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Limit to 90 days
    if (data_fim - data_inicio).days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 90 days"
        )
    
    # Build query
    conditions = [
        Checkin.data_hora >= datetime.combine(data_inicio, datetime.min.time()),
        Checkin.data_hora <= datetime.combine(data_fim, datetime.max.time())
    ]
    
    if usuario_id:
        conditions.append(Checkin.usuario_id == usuario_id)
    
    if status:
        conditions.append(Checkin.status == status)
    
    query = select(Checkin).options(
        selectinload(Checkin.usuario),
        selectinload(Checkin.escala)
    ).where(and_(*conditions)).order_by(Checkin.data_hora.desc())
    
    result = await db.execute(query)
    checkins = result.scalars().all()
    
    # Convert to response format
    report_data = []
    for checkin in checkins:
        report_data.append(RelatorioCheckinResponse(
            id=checkin.id,
            usuario_nome=checkin.usuario.nome,
            usuario_cpf=checkin.usuario.cpf,
            data_plantao=checkin.escala.data_inicio,
            hora_inicio_plantao=checkin.escala.hora_inicio,
            hora_fim_plantao=checkin.escala.hora_fim,
            data_hora_checkin=checkin.data_hora,
            gps_latitude=checkin.gps_lat,
            gps_longitude=checkin.gps_long,
            endereco=checkin.endereco,
            status=checkin.status,
            observacoes=checkin.observacoes
        ))
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="GENERATE_CHECKIN_REPORT",
        details={
            "data_inicio": str(data_inicio),
            "data_fim": str(data_fim),
            "usuario_id": usuario_id,
            "total_records": len(report_data)
        },
        db=db
    )
    
    if export_pdf:
        # TODO: Generate PDF report
        # pdf_content = generate_checkin_pdf_report(report_data, data_inicio, data_fim)
        # return Response(content=pdf_content, media_type="application/pdf")
        pass
    
    return report_data


@router.get("/escalas", response_model=List[RelatorioEscalaResponse])
async def get_escala_report(
    request: Request,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    usuario_id: Optional[int] = Query(None),
    status: Optional[StatusEscalaEnum] = Query(None),
    export_pdf: bool = Query(False),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate schedule report with filters
    Only supervisors and admins can generate reports
    """
    # Validate date range
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Build query
    conditions = [
        Escala.data_inicio >= data_inicio,
        Escala.data_inicio <= data_fim
    ]
    
    if usuario_id:
        conditions.append(Escala.usuario_id == usuario_id)
    
    if status:
        conditions.append(Escala.status == status)
    
    query = select(Escala).options(
        selectinload(Escala.usuario),
        selectinload(Escala.checkins)
    ).where(and_(*conditions)).order_by(Escala.data_inicio.desc(), Escala.hora_inicio.asc())
    
    result = await db.execute(query)
    escalas = result.scalars().all()
    
    # Convert to response format
    report_data = []
    for escala in escalas:
        checkin = escala.checkins[0] if escala.checkins else None
        
        report_data.append(RelatorioEscalaResponse(
            id=escala.id,
            usuario_nome=escala.usuario.nome,
            usuario_cpf=escala.usuario.cpf,
            data=escala.data_inicio,
            hora_inicio=escala.hora_inicio,
            hora_fim=escala.hora_fim,
            status=escala.status,
            observacoes_escala=escala.observacoes,
            tem_checkin=checkin is not None,
            data_hora_checkin=checkin.data_hora if checkin else None,
            status_checkin=checkin.status if checkin else None,
            observacoes_checkin=checkin.observacoes if checkin else None
        ))
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="GENERATE_ESCALA_REPORT",
        details={
            "data_inicio": str(data_inicio),
            "data_fim": str(data_fim),
            "usuario_id": usuario_id,
            "total_records": len(report_data)
        },
        db=db
    )
    
    if export_pdf:
        # TODO: Generate PDF report
        pass
    
    return report_data


@router.get("/horas-trabalhadas", response_model=List[RelatorioHorasResponse])
async def get_horas_report(
    request: Request,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    usuario_id: Optional[int] = Query(None),
    export_pdf: bool = Query(False),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate worked hours report
    Only supervisors and admins can generate reports
    """
    # Validate date range
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Build query to get schedules with check-ins
    conditions = [
        Escala.data_inicio >= data_inicio,
        Escala.data_inicio <= data_fim,
        Escala.status == StatusEscalaEnum.CONFIRMADO  # Only confirmed schedules
    ]
    
    if usuario_id:
        conditions.append(Escala.usuario_id == usuario_id)
    
    query = select(Escala).options(
        selectinload(Escala.usuario),
        selectinload(Escala.checkins)
    ).where(and_(*conditions)).order_by(Escala.usuario_id, Escala.data_inicio)
    
    result = await db.execute(query)
    escalas = result.scalars().all()
    
    # Group by user and calculate hours
    user_hours = {}
    for escala in escalas:
        if not escala.checkins:  # Skip if no check-in
            continue
            
        user_id = escala.usuario_id
        if user_id not in user_hours:
            user_hours[user_id] = {
                'usuario': escala.usuario,
                'total_horas': 0,
                'total_plantoes': 0,
                'detalhes': []
            }
        
        # Calculate hours for this shift
        hora_inicio_dt = datetime.combine(escala.data_inicio, escala.hora_inicio)
        hora_fim_dt = datetime.combine(escala.data_inicio, escala.hora_fim)
        
        # Handle shifts that cross midnight
        if escala.hora_fim <= escala.hora_inicio:
            hora_fim_dt += timedelta(days=1)
        
        horas_plantao = (hora_fim_dt - hora_inicio_dt).total_seconds() / 3600
        
        user_hours[user_id]['total_horas'] += horas_plantao
        user_hours[user_id]['total_plantoes'] += 1
        user_hours[user_id]['detalhes'].append({
            'data': escala.data_inicio,
            'hora_inicio': escala.hora_inicio,
            'hora_fim': escala.hora_fim,
            'horas': horas_plantao,
            'checkin_realizado': len(escala.checkins) > 0
        })
    
    # Convert to response format
    report_data = []
    for user_data in user_hours.values():
        report_data.append(RelatorioHorasResponse(
            usuario_id=user_data['usuario'].id,
            usuario_nome=user_data['usuario'].nome,
            usuario_cpf=user_data['usuario'].cpf,
            periodo_inicio=data_inicio,
            periodo_fim=data_fim,
            total_horas=round(user_data['total_horas'], 2),
            total_plantoes=user_data['total_plantoes'],
            media_horas_por_plantao=round(
                user_data['total_horas'] / user_data['total_plantoes'], 2
            ) if user_data['total_plantoes'] > 0 else 0,
            detalhes_plantoes=user_data['detalhes']
        ))
    
    # Sort by user name
    report_data.sort(key=lambda x: x.usuario_nome)
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="GENERATE_HORAS_REPORT",
        details={
            "data_inicio": str(data_inicio),
            "data_fim": str(data_fim),
            "usuario_id": usuario_id,
            "total_usuarios": len(report_data)
        },
        db=db
    )
    
    if export_pdf:
        # TODO: Generate PDF report
        pass
    
    return report_data


@router.get("/auditoria", response_model=List[RelatorioAuditoria])
async def get_audit_report(
    request: Request,
    data_inicio: datetime = Query(...),
    data_fim: datetime = Query(...),
    usuario_id: Optional[int] = Query(None),
    acao: Optional[str] = Query(None),
    descricao: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate audit log report
    Only supervisors and admins can view audit logs
    """
    # Validate date range
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Limit to 30 days for performance
    if (data_fim - data_inicio).days > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 30 days for audit reports"
        )
    
    # Build query
    conditions = [
        Log.created_at >= data_inicio,
        Log.created_at <= data_fim
    ]
    
    if usuario_id:
        conditions.append(Log.usuario_id == usuario_id)
    
    if acao:
        conditions.append(Log.acao.ilike(f"%{acao}%"))
    
    if descricao:
        conditions.append(Log.descricao.ilike(f"%{descricao}%"))
    
    # Count total
    count_query = select(func.count(Log.id)).where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = select(Log).options(selectinload(Log.usuario)).where(
        and_(*conditions)
    ).offset(offset).limit(per_page).order_by(Log.created_at.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    # Convert to response format
    report_data = []
    for log in logs:
        report_data.append(RelatorioAuditoria(
            id=log.id,
            usuario_nome=log.usuario.nome if log.usuario else "Sistema",
            usuario_email=log.usuario.email if log.usuario else None,
            acao=log.acao,
            descricao=log.descricao,
            data_hora=log.created_at,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            dados_extras=log.dados_extras
        ))
    
    # Log this action (audit of audit!)
    await log_action(
        request=request,
        current_user=current_user,
        action="GENERATE_AUDIT_REPORT",
        details={
            "data_inicio": str(data_inicio),
            "data_fim": str(data_fim),
            "usuario_id": usuario_id,
            "total_records": len(report_data)
        },
        db=db
    )
    
    return report_data


@router.get("/performance")
async def get_performance_report(
    request: Request,
    data_inicio: date = Query(...),
    data_fim: date = Query(...),
    current_user: Usuario = Depends(require_supervisor()),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate performance metrics report
    Only supervisors and admins can view performance metrics
    """
    # User performance metrics
    performance_query = text("""
        SELECT 
            u.id,
            u.nome,
            u.cpf,
            COUNT(DISTINCT e.id) as total_escalas,
            COUNT(DISTINCT c.id) as total_checkins,
            COUNT(DISTINCT CASE WHEN c.status = 'REALIZADO' THEN c.id END) as checkins_ok,
            COUNT(DISTINCT CASE WHEN c.status = 'FORA_DE_LOCAL' THEN c.id END) as checkins_fora_local,
            COUNT(DISTINCT CASE WHEN e.status = 'AUSENTE' THEN e.id END) as faltas,
            ROUND(
                COUNT(DISTINCT CASE WHEN c.status = 'REALIZADO' THEN c.id END) * 100.0 / 
                NULLIF(COUNT(DISTINCT e.id), 0), 2
            ) as taxa_presenca
        FROM usuarios u
        LEFT JOIN escalas e ON u.id = e.usuario_id 
            AND e.data BETWEEN :data_inicio AND :data_fim
        LEFT JOIN checkins c ON e.id = c.escala_id
        WHERE u.perfil = 'SOCIO' AND u.status = 'Ativo'
        GROUP BY u.id, u.nome, u.cpf
        HAVING COUNT(DISTINCT e.id) > 0
        ORDER BY taxa_presenca DESC, u.nome
    """)
    
    result = await db.execute(performance_query, {
        "data_inicio": data_inicio,
        "data_fim": data_fim
    })
    
    performance_data = []
    for row in result:
        performance_data.append({
            "usuario_id": row.id,
            "nome": row.nome,
            "cpf": row.cpf,
            "total_escalas": row.total_escalas,
            "total_checkins": row.total_checkins,
            "checkins_realizados": row.checkins_ok,
            "checkins_fora_local": row.checkins_fora_local,
            "total_faltas": row.faltas,
            "taxa_presenca": float(row.taxa_presenca or 0)
        })
    
    # Overall statistics
    overall_stats = {
        "periodo": {"inicio": data_inicio, "fim": data_fim},
        "total_socios_ativos": len(performance_data),
        "media_taxa_presenca": round(
            sum(p["taxa_presenca"] for p in performance_data) / len(performance_data), 2
        ) if performance_data else 0,
        "melhor_performance": performance_data[0] if performance_data else None,
        "necessita_atencao": [p for p in performance_data if p["taxa_presenca"] < 85]
    }
    
    # Log action
    await log_action(
        request=request,
        current_user=current_user,
        action="GENERATE_PERFORMANCE_REPORT",
        details={
            "data_inicio": str(data_inicio),
            "data_fim": str(data_fim),
            "total_socios": len(performance_data)
        },
        db=db
    )
    
    return {
        "estatisticas_gerais": overall_stats,
        "performance_individual": performance_data
    } 