"""
Pydantic schemas for Schedule (Escala) operations
"""
from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.core.models import StatusEscalaEnum


class EscalaBase(BaseModel):
    """Base schema for schedule data"""
    data_inicio: date
    data_fim: date
    hora_inicio: time
    hora_fim: time
    observacoes: Optional[str] = None
    
    @validator('data_fim')
    def validate_date_range(cls, v, values):
        if 'data_inicio' in values and v < values['data_inicio']:
            raise ValueError('Data fim deve ser posterior ou igual à data início')
        return v


class EscalaCreate(EscalaBase):
    """Schema for creating a new schedule"""
    estabelecimento_id: int
    supervisores_ids: Optional[List[int]] = None  # Lista de IDs dos supervisores


class EscalaUpdate(BaseModel):
    """Schema for updating a schedule"""
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    estabelecimento_id: Optional[int] = None
    status: Optional[StatusEscalaEnum] = None
    observacoes: Optional[str] = None
    supervisores_ids: Optional[List[int]] = None  # Lista de IDs dos supervisores
    
    @validator('data_fim')
    def validate_date_range(cls, v, values):
        if 'data_inicio' in values and values['data_inicio'] and v and v < values['data_inicio']:
            raise ValueError('Data fim deve ser posterior ou igual à data início')
        return v


class EscalaResponse(BaseModel):
    """Schema for schedule response"""
    id: int
    data_inicio: date
    data_fim: date
    hora_inicio: time
    hora_fim: time
    estabelecimento_id: int
    status: StatusEscalaEnum
    observacoes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relacionamentos
    estabelecimento: Optional[dict] = None
    usuarios_atribuidos: Optional[List[dict]] = None
    supervisores: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True


# ========================================
# SCHEMAS PARA RELACIONAMENTO ESCALA-USUÁRIO
# ========================================

class EscalaUsuarioBase(BaseModel):
    """Base schema for escala-usuario relationship"""
    setor_id: int
    status: str = Field(default="Pendente", max_length=50)


class EscalaUsuarioCreate(EscalaUsuarioBase):
    """Schema for creating escala-usuario relationship"""
    usuario_id: int


class EscalaUsuarioUpdate(BaseModel):
    """Schema for updating escala-usuario relationship"""
    setor_id: Optional[int] = None
    status: Optional[str] = Field(None, max_length=50)


class EscalaUsuarioResponse(EscalaUsuarioBase):
    """Schema for escala-usuario relationship response"""
    id: int
    escala_id: int
    usuario_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relacionamentos
    usuario: Optional[dict] = None
    setor: Optional[dict] = None
    
    class Config:
        from_attributes = True


# ========================================
# SCHEMAS PARA LISTAGEM E FILTROS
# ========================================

class EscalaListResponse(BaseModel):
    """Schema for schedule list response"""
    escalas: List[EscalaResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class EscalaFilter(BaseModel):
    """Schema for schedule filters"""
    estabelecimento_id: Optional[int] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    status: Optional[StatusEscalaEnum] = None
    usuario_id: Optional[int] = None  # Para filtrar escalas de um usuário específico
    setor: Optional[str] = None  # Para filtrar por setor
    page: int = 1
    per_page: int = 20


class EscalaStats(BaseModel):
    """Schema for schedule statistics"""
    total_escalas: int
    confirmadas: int
    pendentes: int
    ausentes: int
    percentual_confirmadas: float


class EscalaCalendarView(BaseModel):
    """Schema for calendar view"""
    data: date
    escalas: List[EscalaResponse]


class EscalaBulkCreate(BaseModel):
    """Schema for bulk creating schedules"""
    escalas: List[EscalaCreate]


class EscalaBulkUpdate(BaseModel):
    """Schema for bulk updating schedules"""
    escala_ids: List[int]
    updates: EscalaUpdate 