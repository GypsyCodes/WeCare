# We Care Frontend

Interface React para o Sistema de Gestão Operacional We Care.

## 🚀 Tecnologias

- **React** 18.2.0
- **React Router** 6.3.0
- **Bootstrap** 5.3.0 + React Bootstrap
- **Axios** para requisições HTTP
- **Leaflet** para mapas (GPS)
- **Chart.js** para gráficos
- **React Toastify** para notificações

## 📦 Instalação

### Pré-requisitos
- Node.js 16+ instalado
- Backend We Care rodando na porta 8000

### Instalar dependências
```bash
cd frontend
npm install
```

### Configurar variáveis de ambiente
Crie um arquivo `.env` na pasta `frontend/`:
```
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_APP_NAME=We Care
REACT_APP_VERSION=1.0.0
```

### Executar em desenvolvimento
```bash
npm start
```

Acesse: http://localhost:3000

## 🏗️ Estrutura do Projeto

```
frontend/
├── public/                 # Arquivos públicos
├── src/
│   ├── components/         # Componentes reutilizáveis
│   │   ├── Layout/        # Layout principal
│   │   ├── Auth/          # Componentes de auth
│   │   ├── Dashboard/     # Widgets do dashboard
│   │   ├── Escalas/       # Componentes de escalas
│   │   └── Common/        # Componentes comuns
│   ├── pages/             # Páginas principais
│   │   ├── Auth/          # Login, registro
│   │   ├── Dashboard/     # Dashboard principal
│   │   ├── Escalas/       # Gestão de escalas
│   │   ├── Checkins/      # Check-ins
│   │   ├── Usuarios/      # Gestão de usuários
│   │   ├── Documentos/    # Upload de documentos
│   │   └── Relatorios/    # Relatórios
│   ├── services/          # Serviços da API
│   ├── contexts/          # Context API (estado global)
│   ├── utils/             # Utilitários
│   └── styles/            # Estilos CSS
├── package.json
└── README.md
```

## 🎨 Funcionalidades Principais

### Dashboard Operacional
- ✅ Visualização de escalas
- ✅ Cards de estatísticas
- ✅ Alertas e notificações
- 🔄 Check-in com GPS
- 🔄 Calendário interativo

### Gestão de Usuários
- 🔄 Cadastro hierárquico
- 🔄 Upload de documentos
- 🔄 Processamento OCR
- 🔄 Perfis de permissão

### Sistema de Escalas
- 🔄 Calendário visual
- 🔄 Transferência de plantões
- 🔄 Gestão de ausências

### Relatórios
- 🔄 Gráficos interativos
- 🔄 Exportação PDF
- 🔄 Filtros avançados

## 🔧 Scripts Disponíveis

- `npm start` - Executa em modo desenvolvimento
- `npm build` - Build para produção
- `npm test` - Executa testes
- `npm eject` - Ejeta configurações

## 🌐 Deploy

### Build para produção
```bash
npm run build
```

### Deploy no Vercel/Netlify
1. Conecte o repositório
2. Configure as variáveis de ambiente
3. Build automático a cada push

## 🔐 Autenticação

O sistema usa JWT tokens armazenados no localStorage:

```javascript
// Login
const response = await authService.login({
  email: 'admin@wecare.com',
  senha: 'senha123'
});

// Token é automaticamente incluído nas requisições
```

## 📱 Responsividade

- Desktop: Layout completo com sidebar
- Tablet: Sidebar colapsável
- Mobile: Menu hamburger

## 🎯 Próximos Passos

1. **Instalar dependências**: `npm install`
2. **Configurar .env**: Variáveis de ambiente
3. **Executar**: `npm start`
4. **Implementar páginas**: Seguir TODOs nos arquivos
5. **Conectar com backend**: Testar APIs
6. **Deploy**: Vercel/Netlify

## 📞 Suporte

- Backend deve estar rodando na porta 8000
- Verificar CORS no backend
- Logs no browser console para debug 