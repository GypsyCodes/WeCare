#!/usr/bin/env python3
"""
Script to create the first admin user in the We Care system
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.models import Usuario, PerfilEnum, StatusUsuarioEnum
from app.core.security import get_password_hash


async def create_admin_user():
    """Create the first admin user"""
    
    print("🚀 We Care - Criar Usuário Administrador")
    print("=" * 50)
    
    # Get admin details
    nome = input("Nome completo: ")
    email = input("Email: ")
    cpf = input("CPF (apenas números): ")
    senha = input("Senha: ")
    
    # Validate inputs
    if not nome or not email or not cpf or not senha:
        print("❌ Todos os campos são obrigatórios!")
        return
    
    if len(cpf) != 11 or not cpf.isdigit():
        print("❌ CPF deve conter exatamente 11 números!")
        return
    
    if len(senha) < 8:
        print("❌ Senha deve ter pelo menos 8 caracteres!")
        return
    
    # Format CPF
    cpf_formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin already exists
            from sqlalchemy import select
            result = await db.execute(
                select(Usuario).where(Usuario.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("❌ Já existe um usuário com este email!")
                return
            
            # Check CPF
            result = await db.execute(
                select(Usuario).where(Usuario.cpf == cpf_formatted)
            )
            existing_cpf = result.scalar_one_or_none()
            
            if existing_cpf:
                print("❌ Já existe um usuário com este CPF!")
                return
            
            # Create admin user
            admin_user = Usuario(
                nome=nome,
                email=email,
                cpf=cpf_formatted,
                senha_hash=get_password_hash(senha),
                perfil=PerfilEnum.ADMINISTRADOR,
                status=StatusUsuarioEnum.ATIVO
            )
            
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)
            
            print("✅ Usuário administrador criado com sucesso!")
            print(f"📧 Email: {email}")
            print(f"👤 Nome: {nome}")
            print(f"🆔 ID: {admin_user.id}")
            print("\n🔑 Use estas credenciais para fazer login no sistema.")
            
        except Exception as e:
            print(f"❌ Erro ao criar usuário: {e}")
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(create_admin_user()) 