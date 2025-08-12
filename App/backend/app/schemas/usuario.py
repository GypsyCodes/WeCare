"""
Pydantic schemas for User operations
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

from app.core.models import PerfilEnum, StatusUsuarioEnum


class UsuarioBase(BaseModel):
    """Base schema for user data"""
    nome: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    perfil: PerfilEnum


class UsuarioCreate(UsuarioBase):
    """Schema for creating a user (pre-registration)"""
    cpf: str = Field(..., min_length=11, max_length=14)
    
    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v):
        # Remove formatting
        cpf = re.sub(r'[^\d]', '', v)
        if len(cpf) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        
        # Basic CPF validation algorithm
        def calculate_digit(cpf_partial):
            sum_val = sum(int(cpf_partial[i]) * (len(cpf_partial) + 1 - i) for i in range(len(cpf_partial)))
            remainder = sum_val % 11
            return 0 if remainder < 2 else 11 - remainder
        
        # Check for invalid patterns
        if cpf == cpf[0] * 11:  # All same digits
            raise ValueError('CPF inválido')
        
        # Validate check digits
        if int(cpf[9]) != calculate_digit(cpf[:9]):
            raise ValueError('CPF inválido')
        if int(cpf[10]) != calculate_digit(cpf[:10]):
            raise ValueError('CPF inválido')
        
        # Format CPF with dots and dash
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


class UsuarioRegistrationComplete(BaseModel):
    """Schema for completing user registration"""
    senha: str = Field(..., min_length=8)
    confirmar_senha: str
    telefone: Optional[str] = None
    endereco: Optional[Dict[str, Any]] = None
    dados_profissionais: Optional[Dict[str, Any]] = None
    
    @field_validator('confirmar_senha')
    @classmethod
    def passwords_match(cls, v, info):
        if 'senha' in info.data and v != info.data['senha']:
            raise ValueError('Senhas não conferem')
        return v
    
    @field_validator('senha')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        return v


class UsuarioUpdate(BaseModel):
    """Schema for updating user data"""
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[Dict[str, Any]] = None
    dados_profissionais: Optional[Dict[str, Any]] = None
    status: Optional[StatusUsuarioEnum] = None


class UsuarioChangePassword(BaseModel):
    """Schema for changing user password"""
    senha_atual: str
    nova_senha: str = Field(..., min_length=8)
    confirmar_nova_senha: str
    
    @field_validator('confirmar_nova_senha')
    @classmethod
    def passwords_match(cls, v, info):
        if 'nova_senha' in info.data and v != info.data['nova_senha']:
            raise ValueError('Senhas não conferem')
        return v
    
    @field_validator('nova_senha')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')
        return v


class UsuarioResponse(UsuarioBase):
    """Schema for user response data"""
    id: int
    cpf: str
    status: StatusUsuarioEnum
    documentos: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UsuarioListResponse(BaseModel):
    """Schema for paginated user list response"""
    users: list[UsuarioResponse]
    total: int
    page: int
    per_page: int
    pages: int


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    perfil: Optional[PerfilEnum] = None


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str
    expires_in: int
    user: UsuarioResponse


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    senha: str


class TokenValidationResponse(BaseModel):
    """Schema for token validation response"""
    valid: bool
    user_id: Optional[int] = None
    email: Optional[str] = None
    perfil: Optional[PerfilEnum] = None
    expires_at: Optional[datetime] = None 