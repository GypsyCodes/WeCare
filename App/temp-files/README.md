# Temp Files - We Care

Arquivos temporários e scripts de configuração do projeto We Care.

## 📁 Arquivos Temporários

### `setup_dev.py`
- **Objetivo**: Script de configuração completa do ambiente de desenvolvimento
- **Funcionalidade**: 
  - Verifica dependências (Python, MySQL, etc.)
  - Configura banco de dados
  - Executa migrações
  - Cria usuário administrador
  - Inicia servidor de desenvolvimento
- **Uso**: `python temp-files/setup_dev.py`

### `create_tables.py`
- **Objetivo**: Script alternativo para criar tabelas no banco
- **Funcionalidade**: Usa SQLAlchemy diretamente (bypassa Alembic)
- **Uso**: `python temp-files/create_tables.py`
- **Quando usar**: Se houver problemas com Alembic

## 🔄 Scripts Descontinuados

Estes arquivos foram criados durante o desenvolvimento para resolver problemas específicos:

- ✅ **setup_dev.py**: Script completo de configuração
- ✅ **create_tables.py**: Criação de tabelas via SQLAlchemy
- ❌ **setup_database.py**: Removido (funcionalidade integrada)
- ❌ **test_api_simple.py**: Removido (substituído por test_minimal.py)

## 🎯 Uso Recomendado

### Configuração Inicial Completa
```bash
# Executar script completo de setup
python temp-files\setup_dev.py
```

### Apenas Criar Tabelas
```bash
# Se só precisar criar as tabelas
python temp-files\create_tables.py
```

## ⚠️ Observações

- **Arquivos temporários**: Podem ser removidos após configuração
- **Uso em produção**: NÃO usar estes scripts em produção
- **Backup**: Scripts salvos para referência e debug

## 🗑️ Limpeza

Após a configuração inicial bem-sucedida, você pode:

```bash
# Remover pasta inteira (opcional)
Remove-Item temp-files -Recurse -Force

# Ou manter apenas para referência
# (recomendado durante desenvolvimento)
```

## 📞 Suporte

Se os scripts principais do projeto não funcionarem, use estes arquivos para:
1. Debug de problemas de configuração
2. Setup alternativo de banco de dados
3. Teste de funcionalidades isoladas 