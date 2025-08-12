"""
Database models for We Care system
Based on the specification document
"""
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any
import json

from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Time, Text, 
    ForeignKey, JSON, Enum, Boolean, Table
)
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


# ========================================
# TABELAS DE RELACIONAMENTO
# ========================================

# Tabela de relacionamento entre estabelecimentos e profissionais
estabelecimento_profissionais = Table(
    'estabelecimento_profissionais',
    Base.metadata,
    Column('estabelecimento_id', Integer, ForeignKey('estabelecimentos.id', ondelete='CASCADE'), primary_key=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)

# Tabela de relacionamento entre escalas e supervisores
escala_supervisores = Table(
    'escala_supervisores',
    Base.metadata,
    Column('escala_id', Integer, ForeignKey('escalas.id', ondelete='CASCADE'), primary_key=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)

# Tabela de relacionamento entre escalas e usuários (REFATORADA)
escala_usuarios = Table(
    'escala_usuarios',
    Base.metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('escala_id', Integer, ForeignKey('escalas.id', ondelete='CASCADE'), nullable=False, index=True),
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True),
    Column('setor_id', Integer, ForeignKey('setores.id', ondelete='CASCADE'), nullable=False, index=True),  # Setor específico do usuário nesta escala
    Column('status', String(50), default='Pendente', nullable=False),  # Status individual do usuário
    Column('created_at', DateTime, default=func.now()),
    Column('updated_at', DateTime, onupdate=func.now(), nullable=True)
)


class PerfilEnum(PyEnum):
    ADMINISTRADOR = "Administrador"
    SUPERVISOR = "Supervisor"
    SOCIO = "Socio"


class StatusUsuarioEnum(PyEnum):
    ATIVO = "Ativo"
    INATIVO = "Inativo"


class StatusEscalaEnum(PyEnum):
    PENDENTE = "Pendente"
    CONFIRMADO = "Confirmado"
    AUSENTE = "Ausente"


class StatusCheckinEnum(PyEnum):
    REALIZADO = "Realizado"
    AUSENTE = "Ausente"
    FORA_DE_LOCAL = "Fora de Local"


class Usuario(Base):
    """
    Tabela de usuários do sistema
    Armazena dados de administradores, supervisores e sócios
    """
    __tablename__ = "usuarios"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    perfil: Mapped[PerfilEnum] = mapped_column(Enum(PerfilEnum), nullable=False)
    documentos: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[StatusUsuarioEnum] = mapped_column(
        Enum(StatusUsuarioEnum), 
        default=StatusUsuarioEnum.ATIVO,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        onupdate=func.now(),
        nullable=True
    )
    
    # Relationships
    checkins = relationship("Checkin", back_populates="usuario", cascade="all, delete-orphan")
    documentos_uploaded = relationship("Documento", back_populates="usuario", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="usuario", cascade="all, delete-orphan")
    
    # Relacionamentos many-to-many
    estabelecimentos_trabalha = relationship(
        "Estabelecimento", 
        secondary=estabelecimento_profissionais,
        back_populates="profissionais",
        overlaps="estabelecimentos_trabalha,profissionais"
    )
    
    escalas_supervisionadas = relationship(
        "Escala",
        secondary=escala_supervisores,
        back_populates="supervisores",
        overlaps="escalas_supervisionadas,supervisores"
    )
    
    # Relacionamento many-to-many com escalas atribuídas
    escalas_atribuidas = relationship(
        "Escala",
        secondary=escala_usuarios,
        overlaps="escalas_atribuidas,usuarios_atribuidos"
    )
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, nome='{self.nome}', perfil='{self.perfil}')>"


class Estabelecimento(Base):
    """
    Tabela de estabelecimentos/locais de trabalho
    Define os locais onde os plantões são realizados
    """
    __tablename__ = "estabelecimentos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    longitude: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    raio_checkin: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # metros
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        onupdate=func.now(),
        nullable=True
    )
    
    # Relationships
    escalas = relationship("Escala", back_populates="estabelecimento", cascade="all, delete-orphan")
    setores = relationship("Setor", back_populates="estabelecimento", cascade="all, delete-orphan")
    
    # Relacionamento many-to-many com profissionais
    profissionais = relationship(
        "Usuario",
        secondary=estabelecimento_profissionais,
        back_populates="estabelecimentos_trabalha",
        overlaps="estabelecimentos_trabalha,profissionais"
    )
    
    def __repr__(self):
        return f"<Estabelecimento(id={self.id}, nome='{self.nome}')>"


class Escala(Base):
    """
    Tabela de escalas/plantões
    Define os plantões atribuídos aos usuários
    """
    __tablename__ = "escalas"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_inicio: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    data_fim: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    hora_inicio: Mapped[datetime] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[datetime] = mapped_column(Time, nullable=False)
    estabelecimento_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("estabelecimentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[StatusEscalaEnum] = mapped_column(
        Enum(StatusEscalaEnum),
        default=StatusEscalaEnum.PENDENTE,
        nullable=False
    )
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        onupdate=func.now(),
        nullable=True
    )
    
    # Relationships
    estabelecimento = relationship("Estabelecimento", back_populates="escalas")
    checkins = relationship("Checkin", back_populates="escala", cascade="all, delete-orphan")
    
    # Relacionamento many-to-many com supervisores
    supervisores = relationship(
        "Usuario",
        secondary=escala_supervisores,
        back_populates="escalas_supervisionadas",
        overlaps="escalas_supervisionadas,supervisores"
    )
    
    # Relacionamento many-to-many com múltiplos usuários
    usuarios_atribuidos = relationship(
        "Usuario",
        secondary=escala_usuarios,
        overlaps="escalas_atribuidas,usuarios_atribuidos"
    )
    
    def __repr__(self):
        return f"<Escala(id={self.id}, data_inicio='{self.data_inicio}', data_fim='{self.data_fim}', estabelecimento_id={self.estabelecimento_id})>"


class Checkin(Base):
    """
    Tabela de check-ins operacionais
    Registra check-ins com localização GPS
    """
    __tablename__ = "checkins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    escala_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("escalas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    data_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    gps_lat: Mapped[float] = mapped_column(DECIMAL(10, 8), nullable=False)
    gps_long: Mapped[float] = mapped_column(DECIMAL(11, 8), nullable=False)
    status: Mapped[StatusCheckinEnum] = mapped_column(
        Enum(StatusCheckinEnum),
        default=StatusCheckinEnum.REALIZADO,
        nullable=False
    )
    endereco: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    usuario = relationship("Usuario", back_populates="checkins")
    escala = relationship("Escala", back_populates="checkins")
    
    def __repr__(self):
        return f"<Checkin(id={self.id}, usuario_id={self.usuario_id}, data_hora='{self.data_hora}')>"


class Documento(Base):
    """
    Tabela de documentos dos usuários
    Gerencia arquivos enviados pelos sócios
    """
    __tablename__ = "documentos"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(100), nullable=False)
    arquivo_path: Mapped[str] = mapped_column(String(500), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mimetype: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Relationships
    usuario = relationship("Usuario", back_populates="documentos_uploaded")
    
    def __repr__(self):
        return f"<Documento(id={self.id}, nome_arquivo='{self.nome_arquivo}', usuario_id={self.usuario_id})>"


class Log(Base):
    """
    Tabela de logs do sistema  
    Rastreia todas as ações importantes
    """
    __tablename__ = "logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    acao: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    dados_extras: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    
    # Relationships
    usuario = relationship("Usuario", back_populates="logs")
    
    def __repr__(self):
        return f"<Log(id={self.id}, acao='{self.acao}', usuario_id={self.usuario_id})>"


class Setor(Base):
    """
    Tabela de setores por estabelecimento
    Define os setores disponíveis para atribuição em escalas por estabelecimento
    """
    __tablename__ = "setores"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estabelecimento_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("estabelecimentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )
    
    # Relationships
    estabelecimento = relationship("Estabelecimento", back_populates="setores")
    
    def __repr__(self):
        return f"<Setor(id={self.id}, nome='{self.nome}', estabelecimento_id={self.estabelecimento_id})>"


class TransferenciaPlantao(Base):
    """
    Tabela de transferências de plantão
    Registra transferências entre sócios
    """
    __tablename__ = "transferencias_plantao"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    escala_original_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("escalas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    usuario_origem_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    usuario_destino_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Pendente", nullable=False)
    aprovado_por_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True
    )
    data_aprovacao: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    observacoes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        nullable=True
    )
    
    # Relationships (sem back_populates para evitar conflitos)
    escala_original = relationship("Escala", foreign_keys=[escala_original_id])
    usuario_origem = relationship("Usuario", foreign_keys=[usuario_origem_id])
    usuario_destino = relationship("Usuario", foreign_keys=[usuario_destino_id])
    aprovado_por = relationship("Usuario", foreign_keys=[aprovado_por_id])
    
    def __repr__(self):
        return f"<TransferenciaPlantao(id={self.id}, escala_id={self.escala_original_id}, status='{self.status}')>" 