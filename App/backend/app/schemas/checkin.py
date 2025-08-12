"""
Pydantic schemas for Check-in operations
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.core.models import StatusCheckinEnum


class CheckinBase(BaseModel):
    """Base schema for check-in data"""
    gps_lat: Decimal = Field(..., ge=-90, le=90, decimal_places=8)
    gps_long: Decimal = Field(..., ge=-180, le=180, decimal_places=8)
    endereco: Optional[str] = Field(None, max_length=500)
    observacoes: Optional[str] = None


class CheckinCreate(CheckinBase):
    """Schema for creating a check-in"""
    escala_id: int = Field(..., gt=0)
    
    @validator('gps_lat', 'gps_long')
    def validate_coordinates(cls, v):
        if v is None or v == 0:
            raise ValueError('Coordenadas GPS são obrigatórias')
        return v


class CheckinUpdate(BaseModel):
    """Schema for updating check-in (admin only)"""
    gps_lat: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=8)
    gps_long: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=8)
    status: Optional[StatusCheckinEnum] = None
    endereco: Optional[str] = Field(None, max_length=500)
    observacoes: Optional[str] = None


class CheckinResponse(CheckinBase):
    """Schema for check-in response"""
    id: int
    usuario_id: int
    escala_id: int
    data_hora: datetime
    status: StatusCheckinEnum
    created_at: datetime
    
    # Optional nested data
    usuario: Optional['UsuarioSimpleResponse'] = None
    escala: Optional['EscalaSimpleResponse'] = None
    
    class Config:
        from_attributes = True


class CheckinValidation(BaseModel):
    """Schema for check-in validation"""
    escala_id: int
    gps_lat: Decimal
    gps_long: Decimal
    valid: bool
    message: str
    distance_from_location: Optional[float] = None


class CheckinFilter(BaseModel):
    """Schema for filtering check-ins"""
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    usuario_id: Optional[int] = None
    escala_id: Optional[int] = None
    status: Optional[StatusCheckinEnum] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


class CheckinListResponse(BaseModel):
    """Schema for paginated check-in list"""
    checkins: List[CheckinResponse]
    total: int
    page: int
    per_page: int
    pages: int


class CheckinStats(BaseModel):
    """Schema for check-in statistics"""
    total_checkins: int
    realizados: int
    ausentes: int
    fora_de_local: int
    taxa_presenca: float
    periodo_inicio: datetime
    periodo_fim: datetime


class LocationValidation(BaseModel):
    """Schema for location validation"""
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    address: Optional[str] = None


# Simplified schemas for nested responses
class UsuarioSimpleResponse(BaseModel):
    """Simplified user response"""
    id: int
    nome: str
    email: str
    
    class Config:
        from_attributes = True


class EscalaSimpleResponse(BaseModel):
    """Simplified schedule response"""
    id: int
    data: datetime
    hora_inicio: datetime
    hora_fim: datetime
    
    class Config:
        from_attributes = True


# Update forward references
CheckinResponse.model_rebuild() 