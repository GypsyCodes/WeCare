# Tests - We Care

Scripts de teste para o sistema We Care.

## 📁 Arquivos de Teste

### `test_quick.py`
- **Objetivo**: Teste rápido que termina automaticamente
- **Funcionalidade**: Verifica imports, conexão com DB, e configurações básicas
- **Uso**: `python tests/test_quick.py`

### `test_minimal.py`
- **Objetivo**: FastAPI mínimo sem dependências do projeto
- **Funcionalidade**: Servidor simples para isolar problemas de ambiente
- **Uso**: `python tests/test_minimal.py`

### `test_endpoints.py`
- **Objetivo**: Teste de endpoints HTTP da API
- **Funcionalidade**: Faz requisições para verificar se a API está respondendo
- **Uso**: `python tests/test_endpoints.py` (com servidor rodando)

## 🚀 Como Usar

### 1. Teste Rápido (Recomendado)
```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Executar teste básico
python tests\test_quick.py
```

### 2. Teste de API
```bash
# Em um terminal - iniciar servidor
uvicorn app.main:app --reload

# Em outro terminal - testar endpoints
python tests\test_endpoints.py
```

### 3. Teste Mínimo (Debug)
```bash
# Se houver problemas de ambiente
python tests\test_minimal.py
```

## ✅ Resultados Esperados

### test_quick.py
```
🏗️ We Care - Teste Rápido
==================================================
✅ Imports realizados com sucesso
✅ Configurações carregadas
✅ Conexão com banco de dados estabelecida
✅ Tabelas encontradas: usuarios, escalas, checkins, etc.
🎉 Todos os testes básicos passaram!
```

### test_endpoints.py
```
🧪 Testando Health Check...
✅ Health Check: 200
📝 Resposta: {"status": "healthy", "timestamp": "..."}

🧪 Testando Documentação...
✅ Documentação: 200
📝 Resposta: Página Swagger carregada (HTML)
```

## 🔧 Troubleshooting

### Erro de Importação
- Verificar se o ambiente virtual está ativo
- Verificar se as dependências estão instaladas

### Erro de Conexão DB
- Verificar se o MySQL/XAMPP está rodando
- Verificar credenciais no .env

### Erro de Servidor
- Verificar se a porta 8000 está livre
- Executar como administrador se necessário

## 📋 Checklist de Verificação

- [ ] ✅ Ambiente virtual ativado
- [ ] ✅ MySQL/XAMPP rodando
- [ ] ✅ Dependências instaladas
- [ ] ✅ Arquivo .env configurado
- [ ] ✅ test_quick.py passou
- [ ] ✅ Servidor iniciado sem erros
- [ ] ✅ test_endpoints.py passou 