#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
Sistema We Care - Enfermagem
"""

import asyncio
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Função principal para popular o banco"""
    logger.info("🏥 INICIANDO POPULAÇÃO DO BANCO - SISTEMA DE ENFERMAGEM")
    logger.info("=" * 70)
    
    try:
        # Criar engine de conexão
        engine = create_engine(settings.MYSQL_DATABASE_URL)
        
        logger.info("📋 Etapa 1: Criando tabelas...")
        
        # Verificar se as tabelas existem
        with engine.connect() as conn:
            # Verificar tabelas principais
            tables = ['usuarios', 'estabelecimentos', 'escalas', 'checkins', 'documentos', 'logs', 'escala_usuarios']
            for table in tables:
                try:
                    result = conn.execute(text(f"DESCRIBE `{table}`"))
                    logger.info(f"✅ Tabela {table} existe")
                except Exception as e:
                    logger.error(f"❌ Tabela {table} não existe: {e}")
                    return
        
        logger.info("✅ Tabelas criadas com sucesso")
        
        logger.info("📄 Etapa 2: Executando arquivo SQL...")
        
        # Ler e executar o arquivo SQL corrigido
        sql_file = Path(__file__).parent.parent / "populate_database_fixed.sql"
        
        if not sql_file.exists():
            logger.error(f"❌ Arquivo SQL não encontrado: {sql_file}")
            return
        
        with engine.connect() as conn:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Dividir em comandos individuais
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            logger.info(f"📄 Executando {len(commands)} comandos SQL...")
            
            for i, command in enumerate(commands, 1):
                if command and not command.startswith('--'):
                    try:
                        conn.execute(text(command))
                        logger.info(f"✅ Comando {i}/{len(commands)} executado")
                    except Exception as e:
                        logger.warning(f"⚠️  Erro no comando {i}: {e}")
                        continue
            
            conn.commit()
            logger.info("✅ Arquivo SQL executado com sucesso")
        
        logger.info("🔍 Etapa 3: Verificando dados inseridos...")
        
        # Verificar dados inseridos
        with engine.connect() as conn:
            logger.info("📊 VERIFICAÇÃO DOS DADOS:")
            logger.info("=" * 50)
            
            # Contar registros em cada tabela
            tables = ['usuarios', 'estabelecimentos', 'escalas', 'checkins', 'documentos', 'logs']
            for table in tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"👩‍⚕️ {table.upper()}: {count} registros")
                except Exception as e:
                    logger.error(f"❌ Erro ao contar {table}: {e}")
            
            # Estatísticas por perfil
            try:
                result = conn.execute(text("""
                    SELECT perfil, COUNT(*) as quantidade
                    FROM usuarios
                    GROUP BY perfil
                    ORDER BY quantidade DESC
                """))
                
                logger.info("\n👥 ENFERMEIROS POR PERFIL:")
                for row in result:
                    logger.info(f"   • {row.perfil}: {row.quantidade} enfermeiros")
            except Exception as e:
                logger.error(f"❌ Erro ao buscar estatísticas: {e}")
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 BANCO DE ENFERMAGEM POPULADO COM SUCESSO!")
        logger.info("=" * 70)
        
        logger.info("\n🔑 CREDENCIAIS DE ACESSO:")
        logger.info("   • Admin: admin@wecare.com / admin123")
        logger.info("   • Supervisor: carlos.mendes@wecare.com / 123456")
        logger.info("   • Enfermeira: maria.silva@wecare.com / 123456")
        
        logger.info("\n👩‍⚕️ DADOS INSERIDOS:")
        logger.info("   • 15+ Enfermeiros (Supervisores + Sócios)")
        logger.info("   • 7 Estabelecimentos de Saúde")
        logger.info("   • 20+ Escalas de Plantão")
        logger.info("   • Check-ins com Geolocalização")
        logger.info("   • Documentos (COREN, Certificados)")
        
    except Exception as e:
        logger.error(f"❌ Erro geral: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 