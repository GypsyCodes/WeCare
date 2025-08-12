#!/usr/bin/env python3
"""
Script para executar o servidor We Care
Facilita o desenvolvimento com configurações otimizadas
"""
import os
import sys
import uvicorn
from pathlib import Path

# Adicionar o diretório do projeto ao path (agora está em backend/)
backend_root = Path(__file__).parent
project_root = backend_root.parent
sys.path.insert(0, str(backend_root))
sys.path.insert(0, str(project_root))

def check_environment():
    """Verificar se o ambiente está configurado"""
    env_file = project_root / "config" / ".env"
    
    if not env_file.exists():
        print("❌ Arquivo .env não encontrado!")
        print("💡 Execute: cp config/config.env.example config/.env")
        return False
    
    # Carregar variáveis de ambiente do arquivo correto
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    # Verificar imports básicos
    try:
        from app.main import app
        print("✅ Aplicação carregada com sucesso")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar aplicação: {e}")
        print("💡 Verifique se o ambiente virtual está ativo e as dependências instaladas")
        return False

def main():
    """Função principal"""
    print("🚀 We Care - Servidor de Desenvolvimento")
    print("="*50)
    
    # Verificar ambiente
    if not check_environment():
        sys.exit(1)
    
    # Configurações do servidor
    config = {
        "app": "app.main:app",
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,
        "reload_dirs": [str(backend_root / "app")],
        "log_level": "info",
        "access_log": True,
    }
    
    print(f"🌐 Servidor iniciando em: http://{config['host']}:{config['port']}")
    print(f"📚 Documentação: http://{config['host']}:{config['port']}/docs")
    print(f"🔄 Reload automático: {'Ativado' if config['reload'] else 'Desativado'}")
    print("="*50)
    
    try:
        # Iniciar servidor
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 