import asyncio
from app.core.database import get_db
from sqlalchemy import text

async def check_tables():
    async for db in get_db():
        # Verificar estrutura da tabela setores
        result = await db.execute(text("DESCRIBE setores"))
        print("=== ESTRUTURA TABELA SETORES ===")
        for row in result:
            print(row)
        
        # Verificar estrutura da tabela escala_usuarios
        result = await db.execute(text("DESCRIBE escala_usuarios"))
        print("\n=== ESTRUTURA TABELA ESCALA_USUARIOS ===")
        for row in result:
            print(row)
        
        break

if __name__ == "__main__":
    asyncio.run(check_tables()) 