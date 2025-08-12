# We Care - Estrutura do Projeto Organizada

## 📁 Estrutura Final

```
App/
├── 🏗️ Backend API
│   ├── backend/
│   │   ├── alembic/                # Migrações do banco
│   │   ├── app/                    # Código principal da API
│   │   │   ├── api/v1/            # Endpoints da API
│   │   │   ├── core/              # Configurações e modelos
│   │   │   ├── schemas/           # Validação Pydantic
│   │   │   ├── services/          # Lógica de negócio
│   │   │   └── utils/             # Utilitários
│   │   ├── scripts/               # Scripts de produção
│   │   ├── celery_beat.py         # Tarefas agendadas
│   │   ├── celery_worker.py       # Worker Celery
│   │   ├── run.py                 # Executar servidor
│   │   └── alembic.ini            # Configuração Alembic
│
├── 🎨 Frontend React
│   ├── frontend/
│   │   ├── public/                # Arquivos públicos
│   │   ├── src/                   # Código React
│   │   │   ├── components/        # Componentes reutilizáveis
│   │   │   ├── pages/             # Páginas principais
│   │   │   ├── services/          # API calls
│   │   │   ├── contexts/          # Estado global
│   │   │   └── styles/            # CSS/Estilos
│   │   ├── package.json           # Dependências Node.js
│   │   └── README.md              # Instruções frontend
│
├── 🧪 Testes
│   ├── tests/
│   │   ├── test_quick.py          # Teste rápido (termina automaticamente)
│   │   ├── test_minimal.py        # FastAPI mínimo para debug
│   │   ├── test_endpoints.py      # Teste de endpoints HTTP
│   │   └── README.md              # Instruções de teste
│
├── 📝 Arquivos Temporários
│   ├── temp-files/
│   │   ├── setup_dev.py           # Setup completo do ambiente
│   │   ├── create_tables.py       # Alternativa ao Alembic
│   │   └── README.md              # Documentação dos temp files
│
├── 📚 Documentação
│   └── docs/                      # Documentação do projeto
│
├── ⚙️ Configuração
│   ├── config/
│   │   ├── venv/                  # Ambiente virtual Python
│   │   ├── .env                   # Variáveis de ambiente
│   │   ├── config.env.example     # Template de configuração
│   │   └── requirements.txt       # Dependências Python
│
├── PROJECT_STRUCTURE.md           # Este arquivo
└── README.md                      # Documentação principal
```

## 🎯 Organização por Finalidade

### ✅ **Backend** (pasta `backend/`)
- `app/` - API backend principal
- `scripts/` - Scripts de produção
- `run.py` - Executar aplicação
- `celery_*.py` - Processamento assíncrono
- `alembic/` - Migrações do banco

### 🎨 **Frontend** (pasta `frontend/`)
- Interface React completa
- Independente do backend

### 🧪 **Testes** (pasta `tests/`)
- Scripts de verificação
- Testes de API
- Debug de ambiente

### 🔧 **Desenvolvimento** (pasta `temp-files/`)
- Scripts de configuração
- Ferramentas de setup
- Arquivos de debug

### ⚙️ **Configuração** (pasta `config/`)
- Ambiente virtual Python
- Variáveis de ambiente
- Dependências
- Templates de configuração

### 📋 **Documentação** (raiz)
- README.md principal
- PROJECT_STRUCTURE.md
- Documentação geral

## 🚀 Como Usar

### 1. **Configuração Inicial**
```bash
# Ativar ambiente virtual
config\venv\Scripts\activate

# Instalar dependências
pip install -r config\requirements.txt

# Configurar variáveis
copy config\config.env.example config\.env

# Setup automático
python temp-files\setup_dev.py
```

### 2. **Executar Backend**
```bash
# Ativar ambiente
config\venv\Scripts\activate

# Executar servidor
cd backend
python run.py
# Acesso: http://localhost:8000
```

### 3. **Executar Frontend**
```bash
cd frontend
npm install
npm start
# Acesso: http://localhost:3000
```

### 4. **Testes**
```bash
# Teste rápido
python tests\test_quick.py

# Teste de API (com servidor rodando)
python tests\test_endpoints.py
```

## 📁 Pastas Detalhadas

### Backend (`backend/`)
- **app/**: Código principal da API FastAPI
- **alembic/**: Migrações do banco de dados
- **scripts/**: Scripts de produção e deploy
- **run.py**: Script principal para executar servidor
- **celery_*.py**: Processamento assíncrono com Celery
- **alembic.ini**: Configuração do Alembic

### Frontend (`frontend/src/`)
- **components/**: Componentes React reutilizáveis
- **pages/**: Páginas completas (Dashboard, Login, etc.)
- **services/**: Comunicação com API backend
- **contexts/**: Estado global (Auth, Theme, etc.)
- **styles/**: CSS e temas visuais

### Configuração (`config/`)
- **venv/**: Ambiente virtual Python isolado
- **.env**: Variáveis de ambiente locais
- **config.env.example**: Template de configuração
- **requirements.txt**: Dependências Python

### Testes (`tests/`)
- **test_quick.py**: Verifica imports e conexões
- **test_minimal.py**: FastAPI isolado para debug
- **test_endpoints.py**: Testa rotas da API

### Temporários (`temp-files/`)
- **setup_dev.py**: Configuração automática completa
- **create_tables.py**: Criação direta de tabelas

## ✨ Benefícios da Nova Organização

- ✅ **Separação clara** entre backend, frontend, config e testes
- ✅ **Backend isolado** em sua própria pasta
- ✅ **Configurações centralizadas** na pasta config
- ✅ **Ambiente virtual** organizado dentro de config
- ✅ **Estrutura escalável** para crescimento do projeto
- ✅ **Documentação atualizada** refletindo a estrutura real

## 🔧 Comandos Atualizados

### Ativar Ambiente Virtual
```bash
config\venv\Scripts\activate  # Windows
# ou
source config/venv/bin/activate  # Linux/Mac
```

### Executar Servidor
```bash
cd backend
python run.py
```

### Executar Testes
```bash
# Da raiz do projeto
python tests\test_quick.py
``` 