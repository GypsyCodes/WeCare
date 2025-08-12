#!/usr/bin/env python3
"""
Script para executar o SQL corrigido
"""

import sqlalchemy as sa
from sqlalchemy import text

def main():
    # Conectar ao banco
    engine = sa.create_engine('mysql+pymysql://root:123456@localhost/wecare')
    
    try:
        with engine.connect() as conn:
            print("🔧 Executando script SQL corrigido...")
            
            # Ler o arquivo SQL
            with open('populate_database_fixed.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Executar o SQL
            result = conn.execute(text(sql_content))
            conn.commit()
            
            print("✅ Script SQL executado com sucesso!")
            print("📊 Dados populados no banco de dados")
            
    except Exception as e:
        print(f"❌ Erro ao executar SQL: {e}")

if __name__ == "__main__":
    main() 