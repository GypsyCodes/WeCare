"""
Pydantic schemas for Report operations
"""
from datetime import datetime, date, time
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.models import StatusEscalaEnum, StatusCheckinEnum


class RelatorioFilter(BaseModel):
    """Base schema for report filters"""
    data_inicio: date
    data_fim: date
    usuario_id: Optional[int] = None
    export_pdf: bool = Field(False)


class RelatorioCheckinResponse(BaseModel):
    """Schema for check-in report response"""
    id: int
    usuario_nome: str
    usuario_cpf: str
    data_plantao: date
    hora_inicio_plantao: time
    hora_fim_plantao: time
    data_hora_checkin: datetime
    gps_latitude: Decimal
    gps_longitude: Decimal
    endereco: Optional[str] = None
    status: StatusCheckinEnum
    observacoes: Optional[str] = None


class RelatorioEscalaResponse(BaseModel):
    """Schema for schedule report response"""
    id: int
    usuario_nome: str
    usuario_cpf: str
    data: date
    hora_inicio: time
    hora_fim: time
    status: StatusEscalaEnum
    observacoes_escala: Optional[str] = None
    tem_checkin: bool
    data_hora_checkin: Optional[datetime] = None
    status_checkin: Optional[StatusCheckinEnum] = None
    observacoes_checkin: Optional[str] = None


class PlantaoDetalhe(BaseModel):
    """Schema for shift detail in hours report"""
    data: date
    hora_inicio: time
    hora_fim: time
    horas: float
    checkin_realizado: bool


class RelatorioHorasResponse(BaseModel):
    """Schema for worked hours report response"""
    usuario_id: int
    usuario_nome: str
    usuario_cpf: str
    periodo_inicio: date
    periodo_fim: date
    total_horas: float
    total_plantoes: int
    media_horas_por_plantao: float
    detalhes_plantoes: List[PlantaoDetalhe]


class RelatorioAuditoria(BaseModel):
    """Schema for audit log report"""
    id: int
    usuario_nome: str
    usuario_email: Optional[str] = None
    acao: str
    descricao: str
    data_hora: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    dados_extras: Optional[Dict[str, Any]] = None


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    periodo_inicio: date
    periodo_fim: date
    
    # User statistics
    total_usuarios: int
    usuarios_ativos: int
    total_socios: int
    total_supervisores: int
    
    # Schedule statistics
    total_escalas: int
    escalas_confirmadas: int
    escalas_pendentes: int
    escalas_ausentes: int
    
    # Check-in statistics
    total_checkins: int
    checkins_realizados: int
    checkins_fora_local: int
    checkins_ausentes: int
    taxa_presenca: float
    
    # Document statistics
    total_documentos: int
    documentos_processados: int
    documentos_pendentes: int


class PerformanceUsuario(BaseModel):
    """Schema for individual user performance"""
    usuario_id: int
    nome: str
    cpf: str
    total_escalas: int
    total_checkins: int
    checkins_realizados: int
    checkins_fora_local: int
    total_faltas: int
    taxa_presenca: float


class RelatorioPerformance(BaseModel):
    """Schema for performance report"""
    periodo_inicio: date
    periodo_fim: date
    total_socios_ativos: int
    media_taxa_presenca: float
    melhor_performance: Optional[PerformanceUsuario] = None
    necessita_atencao: List[PerformanceUsuario]
    performance_individual: List[PerformanceUsuario]


class ExportOptions(BaseModel):
    """Schema for export options"""
    format: str = Field("json", pattern="^(json|pdf|excel)$")
    include_details: bool = True
    include_charts: bool = False


class RelatorioRequest(BaseModel):
    """Schema for report generation request"""
    tipo_relatorio: str = Field(..., pattern="^(checkins|escalas|horas|auditoria|performance)$")
    filtros: RelatorioFilter
    opcoes_export: Optional[ExportOptions] = None


class RelatorioMetadata(BaseModel):
    """Schema for report metadata"""
    id: str
    tipo: str
    titulo: str
    descricao: Optional[str] = None
    data_geracao: datetime
    usuario_gerador: str
    periodo_analisado: str
    total_registros: int
    formato: str
    tamanho_bytes: Optional[int] = None


class RelatorioSavedResponse(BaseModel):
    """Schema for saved report response"""
    metadata: RelatorioMetadata
    dados: Optional[Any] = None
    url_download: Optional[str] = None 