"""
Pydantic schemas for Estabelecimento operations
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal


class EstabelecimentoBase(BaseModel):
    """Base schema for estabelecimento data"""
    nome: str = Field(..., min_length=2, max_length=255)
    endereco: str = Field(..., min_length=5, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    raio_checkin: int = Field(default=100, ge=10, le=1000)  # 10m a 1km
    ativo: bool = Field(default=True)


class EstabelecimentoCreate(EstabelecimentoBase):
    """Schema for creating estabelecimento"""
    pass


class EstabelecimentoUpdate(BaseModel):
    """Schema for updating estabelecimento"""
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    endereco: Optional[str] = Field(None, min_length=5, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    raio_checkin: Optional[int] = Field(None, ge=10, le=1000)
    ativo: Optional[bool] = None


class EstabelecimentoResponse(EstabelecimentoBase):
    """Schema for estabelecimento response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EstabelecimentoList(BaseModel):
    """Schema for estabelecimento list response"""
    estabelecimentos: list[EstabelecimentoResponse]
    total: int
    page: int
    size: int
    pages: int 