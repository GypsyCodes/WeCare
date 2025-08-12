#!/usr/bin/env python3
"""
Teste rápido da API We Care - EXECUTA E TERMINA
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_database():
    """Teste rápido do banco de dados"""
    try:
        print("🔧 Testando banco de dados...")
        
        from sqlalchemy import text
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            # Test connection
            result = await db.execute(text("SELECT 1 as test"))
            test_val = result.scalar()
            print(f"✅ Conexão: OK (resultado: {test_val})")
            
            # Count users
            result = await db.execute(text("SELECT COUNT(*) FROM usuarios"))
            user_count = result.scalar()
            print(f"✅ Usuários: {user_count}")
            
            # List tables
            result = await db.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Tabelas: {len(tables)} ({', '.join(tables)})")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        return False

async def test_imports():
    """Teste rápido dos imports"""
    try:
        print("📦 Testando imports...")
        
        from app.core.models import Usuario, Escala, Checkin
        print("✅ Modelos: OK")
        
        from app.core.config import settings
        print(f"✅ Config: OK (DB: {settings.DB_NAME})")
        
        from app.schemas.usuario import UsuarioResponse
        print("✅ Schemas: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

async def main():
    """Função principal - EXECUTA E TERMINA"""
    print("🚀 We Care - Teste Rápido")
    print("="*40)
    
    # Test imports
    import_ok = await test_imports()
    print("-" * 40)
    
    # Test database
    db_ok = await test_database()
    print("-" * 40)
    
    # Summary
    print("📊 RESUMO:")
    print(f"📦 Imports: {'✅ OK' if import_ok else '❌ FAIL'}")
    print(f"🗄️ Banco:   {'✅ OK' if db_ok else '❌ FAIL'}")
    
    if import_ok and db_ok:
        print("\n🎉 TUDO FUNCIONANDO!")
        print("\n📋 Para testar a API completa:")
        print("1. Execute: uvicorn test_api_simple:app --host 127.0.0.1 --port 8000")
        print("2. Abra: http://127.0.0.1:8000/docs")
        print("3. Teste: http://127.0.0.1:8000/test-db")
    else:
        print("\n❌ Há problemas para resolver")
    
    print("\n✅ TESTE CONCLUÍDO - TERMINANDO!")

if __name__ == "__main__":
    asyncio.run(main()) 