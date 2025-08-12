# We Care - Sistema de Gestão Hospitalar

Sistema completo de gestão hospitalar com controle de escalas, check-ins, documentos e relatórios.

## 🚀 Início Rápido (Windows)

```powershell
# 1. Iniciar XAMPP MySQL
# 2. Criar banco "wecare" no phpMyAdmin (nome exato: wecare)

# 3. Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pydantic-settings
copy ..\config\.env .env
python scripts/create_admin_user.py
python run.py

# 4. Frontend (novo terminal)
cd frontend
npm install
npm start

# 5. Criar usuário admin com python scripts/create_admin_user.py
# 6. Login: usar credenciais criadas em http://localhost:3000
```

## 🏗️ Arquitetura

- **Frontend**: React.js na porta 3000
- **Backend**: FastAPI (Python) na porta 8000  
- **Banco de dados**: MySQL (XAMPP local)

## 📋 Pré-requisitos

### Software necessário:
- [Python 3.8+](https://www.python.org/downloads/)
- [Node.js 16+](https://nodejs.org/)
- [XAMPP](https://www.apachefriends.org/) (para MySQL)
- Git

### ⚠️ Importante para Windows:
- Use **PowerShell** (não Command Prompt)
- Todos os comandos foram adaptados para Windows/PowerShell
- Certifique-se que Python e Node estão no PATH

### Verificar instalações:
```powershell
python --version
node --version
npm --version
```

## 🚀 Instalação e Configuração

### 1. Configurar o Banco de Dados (XAMPP)

1. **Iniciar XAMPP**:
   - Abra o XAMPP Control Panel
   - Inicie **Apache** e **MySQL**

2. **Criar banco de dados**:
   - Acesse: http://localhost/phpmyadmin
   - Clique em "Novo" 
   - Nome do banco: `wecare` (exatamente assim, sem underline)
   - Clique em "Criar"

### 2. Configurar o Backend

```powershell
# Navegar para a pasta backend
cd backend

# Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Instalar dependência adicional necessária
pip install pydantic-settings

# Configurar variáveis de ambiente
copy ..\config\.env .env
```

**O arquivo `.env` já está configurado com**:
```env
# Banco de dados
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=
DB_NAME=wecare
DB_PORT=3306

# JWT
SECRET_KEY=change-this-super-secret-key-in-production-min-32-chars

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### 🔧 Configurações Importantes:

#### Banco de Dados:
- **Nome**: `wecare` (exato, sem underline)
- **Usuário**: `root` (padrão XAMPP)
- **Senha**: vazia (padrão XAMPP)
- **Host**: `127.0.0.1:3306`

#### Portas da Aplicação:
- **Frontend React**: `http://localhost:3000`
- **Backend FastAPI**: `http://localhost:8000`
- **Documentação API**: `http://localhost:8000/docs`
- **MySQL (XAMPP)**: `http://localhost/phpmyadmin`

#### Estrutura de Usuários:
- **Administrador**: Acesso total ao sistema
- **Supervisor**: Gestão de escalas e usuários
- **Enfermeiro**: Check-ins e visualizações

**Criar usuário administrador e iniciar servidor**:
```powershell
# Criar usuário administrador (seguir prompts)
python scripts/create_admin_user.py

# Iniciar servidor backend
python run.py
```

> **Nota**: O alembic (migrações) já foi executado. As tabelas já existem no banco.

✅ **Backend funcionando em**: http://localhost:8000
📚 **Documentação da API**: http://localhost:8000/docs

### 3. Configurar o Frontend

**Abrir novo terminal** e navegar para frontend:
```powershell
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm start
```

✅ **Frontend funcionando em**: http://localhost:3000

## 🖥️ URLs Importantes

### Aplicação:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **Documentação**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/redoc

### Desenvolvimento:
- **phpMyAdmin**: http://localhost/phpmyadmin
- **XAMPP Control**: Abrir XAMPP Control Panel

### Credenciais de Acesso:
- **Sistema**: ⚠️ **CRIAR PRIMEIRO** com o script
- **MySQL**: root / (sem senha)
- **phpMyAdmin**: root / (sem senha)

## 🔐 Primeiro Acesso

### ⚠️ IMPORTANTE: Criar Usuário Administrador

**As credenciais NÃO existem por padrão!** Você deve criá-las primeiro:

1. **Execute o script de criação**:
   ```powershell
   cd backend
   venv\Scripts\activate
   python scripts/create_admin_user.py
   ```

2. **Preencha os dados quando solicitado**:
   ```
   Nome completo: Administrador
   Email: admin@wecare.com
   Senha: admin123
   Confirmar senha: admin123
   Perfil: administrador
   ```

3. **Aguarde a confirmação**: `✅ Usuário criado com sucesso!`

### Fluxo de login:
1. **Acesse**: http://localhost:3000
2. **Use as credenciais que você CRIOU**:
   - Email: `admin@wecare.com`
   - Senha: `admin123` (ou a que você definiu)
3. **Será redirecionado** para o dashboard principal

### 🎨 Interface de Login:
- ✅ **Design moderno** com gradientes
- ✅ **Responsivo** para mobile e desktop  
- ✅ **Animações suaves** de entrada
- ✅ **Feedback visual** para carregamento

## 📱 Funcionalidades Disponíveis

### ✅ Implementadas:
- **🔐 Autenticação**: Login/logout com JWT + design moderno
- **📊 Dashboard**: Visão geral do sistema
- **👥 Gestão de Usuários**: Sistema de criação e listagem
- **📅 Escalas**: Estrutura completa preparada
- **📍 Check-ins**: Sistema com GPS preparado
- **📄 Documentos**: Upload e gestão preparados
- **📈 Relatórios**: Geração e visualização preparados
- **🎨 Interface**: Design responsivo com Bootstrap + CSS custom

### 🚧 Em Desenvolvimento:
- CRUD completo de usuários
- Sistema de escalas com calendário
- Check-ins com GPS
- Upload de documentos
- Geração de relatórios PDF
- Notificações em tempo real

## 🗂️ Estrutura do Projeto

```
We Care/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # Endpoints da API
│   │   ├── core/                 # Configurações
│   │   ├── models/               # Modelos do banco
│   │   ├── schemas/              # Validação Pydantic
│   │   └── services/             # Lógica de negócio
│   ├── alembic/                  # Migrações
│   ├── scripts/                  # Scripts utilitários
│   └── run.py                    # Inicializar servidor
├── frontend/
│   ├── src/
│   │   ├── components/           # Componentes React
│   │   ├── pages/                # Páginas da aplicação
│   │   ├── services/             # Serviços de API
│   │   └── styles/               # Estilos CSS
│   └── package.json
├── config/
│   └── .env                      # Variáveis de ambiente
└── README.md
```

## 🔧 Comandos Úteis

### Backend:
```powershell
cd backend

# Ativar ambiente virtual
venv\Scripts\activate

# Rodar servidor
python run.py

# Nova migração
alembic revision --autogenerate -m "descrição"

# Aplicar migrações
alembic upgrade head

# Criar usuário admin
python scripts/create_admin_user.py
```

### Frontend:
```powershell
cd frontend

# Instalar nova dependência
npm install nome-do-pacote

# Rodar servidor
npm start

# Build para produção
npm run build
```

## 🐛 Troubleshooting

### Erro de conexão com banco:
1. Verificar se XAMPP MySQL está rodando
2. Confirmar credenciais no `.env`
3. Testar conexão: http://localhost/phpmyadmin

### Erro "Module not found":
1. Verificar se está na pasta correta (`cd frontend` ou `cd backend`)
2. Reinstalar dependências (`npm install` ou `pip install -r requirements.txt`)

### Erro de CORS:
1. Verificar se backend está rodando na porta 8000
2. Confirmar configuração de proxy no `frontend/package.json`

### Backend não inicia:
1. Ativar ambiente virtual: `venv\Scripts\activate`
2. Verificar se o banco existe
3. Rodar migrações: `alembic upgrade head`

### Problemas específicos do Windows:
1. **"Scripts\activate" não funciona**: Use PowerShell como administrador
2. **Erro de política de execução**: Execute `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. **Python não reconhecido**: Instale Python via Microsoft Store ou adicione ao PATH
4. **Node não reconhecido**: Reinicie o terminal após instalar o Node.js
5. **SECRET_KEY não encontrado**: Execute `copy ..\config\.env .env` na pasta backend
6. **pydantic_settings não encontrado**: Execute `pip install pydantic-settings`

### Comandos PowerShell úteis:
```powershell
# Ver diretório atual
pwd

# Listar arquivos
dir

# Limpar terminal
cls

# Ver processos rodando na porta 3000/8000
netstat -an | findstr ":3000"
netstat -an | findstr ":8000"
```

## 📞 Suporte

Em caso de problemas:
1. **Verificar logs** do terminal (frontend e backend)
2. **API Docs**: http://localhost:8000/docs
3. **Verificar servidores**: Ambos devem estar rodando
4. **Testar endpoints**: http://localhost:8000/api/v1/auth/login
5. **Banco de dados**: http://localhost/phpmyadmin

### ✅ Checklist de Funcionamento:
- [ ] XAMPP MySQL iniciado
- [ ] Banco `wecare` criado  
- [ ] Backend rodando na porta 8000
- [ ] Frontend rodando na porta 3000
- [ ] Usuário admin criado
- [ ] Login funcionando

### 🎯 Próximos Passos:
1. **Teste o sistema**: Faça login e navegue
2. **Crie usuários**: Use o sistema de gestão
3. **Explore módulos**: Escalas, check-ins, etc.
4. **Desenvolvimento**: Implemente funcionalidades completas

---

**Desenvolvido pela Gypsy Codes - à empresa We Care** 🏥 