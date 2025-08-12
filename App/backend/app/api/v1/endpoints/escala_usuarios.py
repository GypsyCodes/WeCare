"""
Escala-Usuario relationship management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.models import Escala, Usuario, escala_usuarios
from app.core.deps import get_current_user, require_supervisor
from app.schemas.escala import (
    EscalaUsuarioCreate, EscalaUsuarioUpdate, EscalaUsuarioResponse
)

router = APIRouter()


@router.post("/{escala_id}/usuarios", response_model=EscalaUsuarioResponse)
async def adicionar_usuario_escala(
    escala_id: int,
    dados: EscalaUsuarioCreate,
    current_user: Usuario = Depends(require_supervisor),
    db: AsyncSession = Depends(get_db)
):
    """Adicionar usuário a uma escala"""
    
    # Verificar se a escala existe
    escala = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = escala.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Verificar se o usuário existe
    usuario = await db.execute(
        select(Usuario).where(Usuario.id == dados.usuario_id)
    )
    usuario = usuario.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar se o usuário já está atribuído à escala
    existing = await db.execute(
        select(escala_usuarios).where(
            and_(
                escala_usuarios.c.escala_id == escala_id,
                escala_usuarios.c.usuario_id == dados.usuario_id
            )
        )
    )
    
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuário já está atribuído a esta escala"
        )
    
    # Inserir relacionamento
    stmt = escala_usuarios.insert().values(
        escala_id=escala_id,
        usuario_id=dados.usuario_id,
        setor=dados.setor,
        status=dados.status
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    # Retornar dados do relacionamento criado
    relacionamento = await db.execute(
        select(escala_usuarios).where(escala_usuarios.c.id == result.inserted_primary_key[0])
    )
    
    return relacionamento.scalar_one_or_none()


@router.get("/{escala_id}/usuarios", response_model=List[EscalaUsuarioResponse])
async def listar_usuarios_escala(
    escala_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar usuários atribuídos a uma escala"""
    
    # Verificar se a escala existe
    escala = await db.execute(
        select(Escala).where(Escala.id == escala_id)
    )
    escala = escala.scalar_one_or_none()
    
    if not escala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escala não encontrada"
        )
    
    # Buscar relacionamentos com dados do usuário
    stmt = select(escala_usuarios).where(escala_usuarios.c.escala_id == escala_id)
    result = await db.execute(stmt)
    relacionamentos = result.fetchall()
    
    # Buscar dados dos usuários
    usuarios_ids = [r.usuario_id for r in relacionamentos]
    usuarios = await db.execute(
        select(Usuario).where(Usuario.id.in_(usuarios_ids))
    )
    usuarios_dict = {u.id: u for u in usuarios.scalars().all()}
    
    # Montar resposta
    response = []
    for rel in relacionamentos:
        usuario = usuarios_dict.get(rel.usuario_id)
        response.append({
            "id": rel.id,
            "escala_id": rel.escala_id,
            "usuario_id": rel.usuario_id,
            "setor": rel.setor,
            "status": rel.status,
            "created_at": rel.created_at,
            "updated_at": rel.updated_at,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": usuario.perfil.value
            } if usuario else None
        })
    
    return response


@router.put("/{escala_id}/usuarios/{usuario_id}", response_model=EscalaUsuarioResponse)
async def atualizar_usuario_escala(
    escala_id: int,
    usuario_id: int,
    dados: EscalaUsuarioUpdate,
    current_user: Usuario = Depends(require_supervisor),
    db: AsyncSession = Depends(get_db)
):
    """Atualizar dados do usuário na escala"""
    
    # Verificar se o relacionamento existe
    existing = await db.execute(
        select(escala_usuarios).where(
            and_(
                escala_usuarios.c.escala_id == escala_id,
                escala_usuarios.c.usuario_id == usuario_id
            )
        )
    )
    relacionamento = existing.scalar_one_or_none()
    
    if not relacionamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não está atribuído a esta escala"
        )
    
    # Preparar dados para atualização
    update_data = {}
    if dados.setor is not None:
        update_data["setor"] = dados.setor
    if dados.status is not None:
        update_data["status"] = dados.status
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado fornecido para atualização"
        )
    
    # Atualizar relacionamento
    stmt = escala_usuarios.update().where(
        and_(
            escala_usuarios.c.escala_id == escala_id,
            escala_usuarios.c.usuario_id == usuario_id
        )
    ).values(**update_data)
    
    await db.execute(stmt)
    await db.commit()
    
    # Retornar dados atualizados
    updated = await db.execute(
        select(escala_usuarios).where(
            and_(
                escala_usuarios.c.escala_id == escala_id,
                escala_usuarios.c.usuario_id == usuario_id
            )
        )
    )
    
    return updated.scalar_one_or_none()


@router.delete("/{escala_id}/usuarios/{usuario_id}")
async def remover_usuario_escala(
    escala_id: int,
    usuario_id: int,
    current_user: Usuario = Depends(require_supervisor),
    db: AsyncSession = Depends(get_db)
):
    """Remover usuário de uma escala"""
    
    # Verificar se o relacionamento existe
    existing = await db.execute(
        select(escala_usuarios).where(
            and_(
                escala_usuarios.c.escala_id == escala_id,
                escala_usuarios.c.usuario_id == usuario_id
            )
        )
    )
    relacionamento = existing.scalar_one_or_none()
    
    if not relacionamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não está atribuído a esta escala"
        )
    
    # Remover relacionamento
    stmt = escala_usuarios.delete().where(
        and_(
            escala_usuarios.c.escala_id == escala_id,
            escala_usuarios.c.usuario_id == usuario_id
        )
    )
    
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Usuário removido da escala com sucesso"}


@router.get("/usuarios/{usuario_id}/escalas", response_model=List[dict])
async def listar_escalas_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Listar escalas de um usuário específico"""
    
    # Verificar se o usuário existe
    usuario = await db.execute(
        select(Usuario).where(Usuario.id == usuario_id)
    )
    usuario = usuario.scalar_one_or_none()
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Buscar escalas do usuário
    stmt = select(escala_usuarios, Escala).join(
        Escala, escala_usuarios.c.escala_id == Escala.id
    ).where(escala_usuarios.c.usuario_id == usuario_id)
    
    result = await db.execute(stmt)
    escalas_usuario = result.fetchall()
    
    # Montar resposta
    response = []
    for rel, escala in escalas_usuario:
        response.append({
            "escala": {
                "id": escala.id,
                "data_inicio": escala.data_inicio,
                "data_fim": escala.data_fim,
                "hora_inicio": escala.hora_inicio,
                "hora_fim": escala.hora_fim,
                "estabelecimento_id": escala.estabelecimento_id,
                "status": escala.status.value,
                "observacoes": escala.observacoes
            },
            "setor": rel.setor,
            "status_usuario": rel.status,
            "created_at": rel.created_at
        })
    
    return response 