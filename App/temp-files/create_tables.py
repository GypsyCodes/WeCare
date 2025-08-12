#!/usr/bin/env python3
"""
Script para criar tabelas diretamente usando SQLAlchemy
Alternativa ao Alembic para casos onde há problemas de configuração
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import engine
from app.core.models import Base

async def create_tables():
    """Criar todas as tabelas do banco de dados"""
    try:
        print("🚀 Iniciando criação das tabelas...")
        
        # Create all tables
        async with engine.begin() as conn:
            print("🔗 Conectado ao banco de dados")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Todas as tabelas foram criadas com sucesso!")
        
        # List created tables
        async with engine.begin() as conn:
            result = await conn.execute("SHOW TABLES")
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"\n📋 Tabelas criadas ({len(tables)}):")
                for table in tables:
                    print(f"  ✓ {table}")
            else:
                print("❌ Nenhuma tabela encontrada")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    
    finally:
        await engine.dispose()

async def main():
    """Função principal"""
    print("🏗️ We Care - Criação de Tabelas")
    print("="*50)
    
    success = await create_tables()
    
    if success:
        print("\n🎉 Configuração concluída!")
        print("\n📋 Próximos passos:")
        print("1. Execute: python scripts/create_admin_user.py")
        print("2. Execute: uvicorn app.main:app --reload")
        print("3. Acesse: http://localhost:8000/docs")
    else:
        print("\n❌ Configuração falhou!")
        print("Verifique se o MySQL está rodando no XAMPP")
        
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 