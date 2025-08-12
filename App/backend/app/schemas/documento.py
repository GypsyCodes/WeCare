"""
Pydantic schemas for Document operations
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DocumentoBase(BaseModel):
    """Base schema for document data"""
    tipo_documento: str = Field(..., max_length=50)
    nome_arquivo: str = Field(..., max_length=255)


class DocumentoResponse(DocumentoBase):
    """Schema for document response"""
    id: int
    usuario_id: int
    arquivo_url: str
    arquivo_path: Optional[str] = None
    tamanho_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    processado: bool = False
    dados_extraidos: Optional[Dict[str, Any]] = None
    data_upload: datetime
    
    # Optional nested user data
    usuario: Optional['UsuarioSimpleResponse'] = None
    
    class Config:
        from_attributes = True


class DocumentoCreate(DocumentoBase):
    """Schema for creating a document (used internally)"""
    usuario_id: int
    arquivo_url: str
    arquivo_path: Optional[str] = None
    tamanho_bytes: Optional[int] = None
    mime_type: Optional[str] = None


class DocumentoUpdate(BaseModel):
    """Schema for updating document data"""
    tipo_documento: Optional[str] = Field(None, max_length=50)
    processado: Optional[bool] = None
    dados_extraidos: Optional[Dict[str, Any]] = None


class DocumentoFilter(BaseModel):
    """Schema for filtering documents"""
    usuario_id: Optional[int] = None
    tipo_documento: Optional[str] = None
    processado: Optional[bool] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


class DocumentoListResponse(BaseModel):
    """Schema for paginated document list"""
    documentos: List[DocumentoResponse]
    total: int
    page: int
    per_page: int
    pages: int


class DocumentoUpload(BaseModel):
    """Schema for document upload request"""
    tipo_documento: str = Field(..., max_length=50)
    usuario_id: Optional[int] = None


class DocumentoProcessingResult(BaseModel):
    """Schema for OCR/NLP processing results"""
    documento_id: int
    success: bool
    dados_extraidos: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None


class DocumentoType(BaseModel):
    """Schema for document type definition"""
    code: str
    name: str
    required: bool
    description: Optional[str] = None


class DocumentoStats(BaseModel):
    """Schema for document statistics"""
    total_documentos: int
    processados: int
    pendentes: int
    usuarios_com_documentos: int
    distribuicao_por_tipo: Dict[str, int]


# Simplified schemas for nested responses
class UsuarioSimpleResponse(BaseModel):
    """Simplified user response"""
    id: int
    nome: str
    email: str
    
    class Config:
        from_attributes = True


# Update forward references
DocumentoResponse.model_rebuild() 