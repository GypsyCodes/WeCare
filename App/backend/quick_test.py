#!/usr/bin/env python3
"""
Teste rápido do banco
"""
import pymysql

def test_database():
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='wecare',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Listar tabelas
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📊 Tabelas: {[t[0] for t in tables]}")
            
            # Verificar usuário admin
            cursor.execute("SELECT id, nome, email, perfil FROM usuarios WHERE email = 'admin@wecare.com'")
            user = cursor.fetchone()
            
            if user:
                print(f"✅ Admin encontrado: {user[1]} ({user[2]}) - {user[3]}")
                return True
            else:
                print("❌ Admin não encontrado!")
                return False
                
        connection.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_database() 