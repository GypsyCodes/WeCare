"""
Pydantic schemas for Setor operations
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SetorBase(BaseModel):
    """Base schema for setor data"""
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = None
    estabelecimento_id: int
    ativo: bool = True


class SetorCreate(SetorBase):
    """Schema for creating a new setor"""
    pass


class SetorUpdate(BaseModel):
    """Schema for updating a setor"""
    nome: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = None
    ativo: Optional[bool] = None


class SetorResponse(SetorBase):
    """Schema for setor response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relacionamentos
    estabelecimento: Optional[dict] = None
    
    class Config:
        from_attributes = True


class SetorListResponse(BaseModel):
    """Schema for setor list response"""
    setores: list[SetorResponse]
    total: int
    page: int
    per_page: int
    pages: int 