#!/usr/bin/env python3
"""
🏥 Setup completo do banco de dados We Care
Recria tudo do zero de forma organizada
"""
import pymysql
import bcrypt
import subprocess
import sys
import os
from datetime import datetime

def print_step(step_num, title, description=""):
    """Imprimir etapa com formatação bonita"""
    print(f"\n{'='*60}")
    print(f"📋 ETAPA {step_num}: {title}")
    if description:
        print(f"💡 {description}")
    print(f"{'='*60}")

def create_database():
    """Criar banco de dados We Care"""
    print_step(1, "CRIANDO BANCO DE DADOS", "Conectando ao MySQL e criando banco 'wecare'")
    
    try:
        # Conectar ao MySQL sem especificar banco
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Criar banco se não existir
            cursor.execute("CREATE DATABASE IF NOT EXISTS wecare CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("USE wecare")
            
            # Verificar se foi criado
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            
            print(f"✅ Banco '{db_name}' criado/conectado com sucesso!")
            
        connection.commit()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        return False

def init_alembic():
    """Inicializar Alembic do zero"""
    print_step(2, "INICIALIZANDO ALEMBIC", "Configurando controle de versão do banco")
    
    try:
        # Gerar migração inicial
        print("🔨 Gerando migração inicial...")
        result = subprocess.run([
            sys.executable, "-m", "alembic", "revision", "--autogenerate", 
            "-m", "initial_migration_clean"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Migração inicial gerada!")
            print(f"📄 Saída: {result.stdout}")
        else:
            print(f"❌ Erro ao gerar migração: {result.stderr}")
            return False
            
        # Aplicar migração
        print("🚀 Aplicando migração...")
        result = subprocess.run([
            sys.executable, "-m", "alembic", "upgrade", "head"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Migração aplicada com sucesso!")
            print(f"📄 Saída: {result.stdout}")
            return True
        else:
            print(f"❌ Erro ao aplicar migração: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no Alembic: {e}")
        return False

def verify_tables():
    """Verificar se as tabelas foram criadas"""
    print_step(3, "VERIFICANDO TABELAS", "Validando estrutura do banco")
    
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
            
            print(f"📊 Tabelas criadas ({len(tables)}):")
            for table in tables:
                print(f"   ✅ {table[0]}")
            
            # Verificar tabela usuarios especificamente
            cursor.execute("DESCRIBE usuarios")
            columns = cursor.fetchall()
            
            print(f"\n👤 Estrutura da tabela usuarios ({len(columns)} campos):")
            for col in columns:
                print(f"   • {col[0]} ({col[1]})")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def create_admin_user():
    """Criar usuário administrador"""
    print_step(4, "CRIANDO USUÁRIO ADMIN", "Usuário administrador padrão do sistema")
    
    try:
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='wecare',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Verificar se já existe admin
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'ADMINISTRADOR'")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print("ℹ️  Usuário admin já existe, removendo para recriar...")
                cursor.execute("DELETE FROM usuarios WHERE perfil = 'ADMINISTRADOR'")
            
            # Gerar hash da senha
            senha = "admin123"
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Inserir admin
            cursor.execute("""
                INSERT INTO usuarios (
                    nome, cpf, email, senha_hash, perfil, status, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                'Administrador Sistema',
                '00000000000',
                'admin@wecare.com?',
                senha_hash,
                'ADMINISTRADOR',
                'ATIVO',
                datetime.now()
            ))
            
            print("✅ Usuário admin criado com sucesso!")
            print("\n🔐 CREDENCIAIS DE LOGIN:")
            print("   📧 Email: admin@wecare.com")
            print("   🔒 Senha: admin123")
            
        connection.commit()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        return False

def test_system():
    """Testar se o sistema está funcionando"""
    print_step(5, "TESTANDO SISTEMA", "Validação final do setup")
    
    try:
        # Testar autenticação direta
        connection = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='wecare',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, nome, email, senha_hash 
                FROM usuarios 
                WHERE email = 'admin@wecare.com'
            """)
            
            user = cursor.fetchone()
            if user:
                # Testar senha
                senha_valida = bcrypt.checkpw(
                    "admin123".encode('utf-8'), 
                    user[3].encode('utf-8')
                )
                
                if senha_valida:
                    print("✅ Autenticação testada - FUNCIONANDO!")
                    print(f"👤 Usuário: {user[1]} (ID: {user[0]})")
                else:
                    print("❌ Problema na autenticação!")
                    return False
            else:
                print("❌ Usuário admin não encontrado!")
                return False
        
        connection.close()
        
        print("\n🎉 SISTEMA CONFIGURADO COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Inicie o servidor: python -m uvicorn app.main:app --reload")
        print("2. Acesse: http://localhost:8000/docs")
        print("3. Teste o login com as credenciais acima")
        print("4. Frontend: http://localhost:3000")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🏥 CONFIGURAÇÃO COMPLETA DO SISTEMA WE CARE")
    print("🚀 Recriando banco de dados do zero...")
    
    # Executar todas as etapas
    steps = [
        create_database,
        init_alembic,
        verify_tables,
        create_admin_user,
        test_system
    ]
    
    for i, step in enumerate(steps, 1):
        if not step():
            print(f"\n❌ FALHA NA ETAPA {i}! Parando execução...")
            return False
    
    print(f"\n{'🎉'*20}")
    print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"{'🎉'*20}")
    
    return True

if __name__ == "__main__":
    main() 