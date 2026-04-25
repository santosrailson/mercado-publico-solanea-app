# Mercado Público - Sistema de Gestão

Sistema moderno de gestão para o Mercado Público de Solânea - PB. 

Arquitetura separada em backend (Python/FastAPI) e frontend (React/TypeScript), containerizado com Docker.

## 🏗️ Arquitetura

```
mercado-publico/
├── backend/              # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/         # Rotas/endpoints
│   │   ├── core/        # Configurações e segurança
│   │   ├── crud/        # Operações de banco
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # PDF, Excel
│   └── Dockerfile
├── frontend/            # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/  # Componentes UI
│   │   ├── pages/       # Páginas
│   │   ├── services/    # API clients
│   │   └── store/       # Zustand stores
│   └── Dockerfile
└── docker-compose.yml
```

## 🚀 Tecnologias

### Backend
- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy 2.0** - ORM para banco de dados
- **Pydantic** - Validação de dados
- **JWT** - Autenticação stateless
- **ReportLab** - Geração de PDFs
- **OpenPyXL** - Geração de Excel

### Frontend
- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool rápida
- **TanStack Query** - Gerenciamento de estado server
- **Zustand** - Gerenciamento de estado client
- **Tailwind CSS** - Estilos utilitários
- **Recharts** - Gráficos

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração

## 📦 Funcionalidades

- ✅ Dashboard com KPIs e gráficos
- ✅ Gestão de cessionários/feirantes
- ✅ Controle de pagamentos
- ✅ Relatórios em PDF e Excel
- ✅ Certidões de situação
- ✅ Autenticação JWT
- ✅ Temas claro/escuro
- ✅ Design responsivo

## 🛠️ Setup

### Via Docker (Recomendado)

```bash
# Clone o repositório
git clone <repo-url>
cd mercado-publico

# Suba os containers
docker-compose up -d

# Acesse
# Frontend: http://localhost
# API Docs: http://localhost:8000/docs
```

### Desenvolvimento Local

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔑 Primeiro Acesso

1. Acesse o sistema em `http://localhost`
2. Crie um usuário inicial via API ou use o endpoint de seed
3. Faça login com as credenciais criadas

## 📚 Documentação da API

Com o backend rodando, acesse:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testes

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## 📝 Estrutura do Banco

O sistema utiliza SQLite por padrão (fácil de migrar para PostgreSQL):

- **users** - Usuários do sistema
- **cessionarios** - Cessionários e feirantes
- **pagamentos** - Registro de pagamentos

## 🎨 Design System

- Cores primárias: Verde-água (#00c896)
- Tema escuro: Azul-marinho (#07111e)
- Tipografia: Inter
- Componentes reutilizáveis em `frontend/src/components/ui/`

## 🔒 Segurança

- Autenticação JWT com expiração
- Senhas hasheadas com bcrypt
- CORS configurado
- SQL injection protegido via ORM
- XSS protegido via React

## 🚀 Deploy

### Produção com Docker

```bash
# Build otimizado
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Variáveis de Ambiente

```env
# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@db/mercado
CORS_ORIGINS=["https://yourdomain.com"]

# Frontend
VITE_API_URL=https://api.yourdomain.com
```

## 📄 Licença

Sistema desenvolvido para o Mercado Público de Solânea - PB.

---

**Desenvolvido com:** Python + React + Docker

**Melhorias profissionais (FastAPI + React):** Implementadas com auxílio do Kimi 2.5
