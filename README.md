# Mercado Público - Sistema de Gestão

Sistema profissional de gestão para o Mercado Público de Solânea - PB, reconstruído para alta performance e segurança.

Arquitetura moderna separada em backend (Python/FastAPI) e frontend (React/TypeScript), containerizada com Docker e persistência em PostgreSQL.

## 🏗️ Arquitetura

```
mercado-publico-solanea-app/
├── backend/              # FastAPI + SQLAlchemy + PostgreSQL
│   ├── alembic/         # Migrações de banco de dados
│   ├── app/
│   │   ├── api/         # Rotas/endpoints (com Rate Limiting)
│   │   ├── core/        # Configurações e segurança (JWT + Bcrypt)
│   │   ├── crud/        # Operações de banco
│   │   ├── models/      # SQLAlchemy models (incluindo AuditLog)
│   │   ├── schemas/     # Pydantic schemas
│   │   └── services/    # PDF, Excel
│   ├── scripts/         # Scripts utilitários (Migração SQLite -> Postgres)
│   ├── tests/           # Testes unitários e integração (Pytest)
│   └── Dockerfile
├── frontend/            # React + TypeScript + Vite (Otimizado)
│   ├── src/
│   │   ├── components/  # Componentes UI (Code Splitting/Lazy Loading)
│   │   ├── pages/       # Páginas (Lazy Loaded)
│   │   ├── services/    # API clients
│   │   └── store/       # Zustand stores
│   └── Dockerfile       # PWA Support
└── docker-compose.yml   # Orquestração (DB, Backend, Frontend)
```

## 🚀 Tecnologias

### Backend (Produção)
- **FastAPI** - Framework web moderno e ultra-rápido
- **PostgreSQL** - Banco de dados relacional robusto para produção
- **SQLAlchemy 2.0** - ORM moderno
- **Alembic** - Gestão de versões de banco de dados (Migrações)
- **SlowAPI** - Proteção de Rate Limiting (Anti Brute-Force)
- **Pytest** - Suíte de testes automatizados
- **JWT** - Autenticação stateless segura

### Frontend (Otimizado)
- **React 18** - Biblioteca UI
- **React Lazy / Suspense** - Carregamento sob demanda (Code Splitting)
- **Vite PWA** - Suporte a Progressive Web App (Instalável no celular)
- **TypeScript** - Segurança de tipos
- **TanStack Query** - Cache e gerenciamento de estado assíncrono

## 📦 Funcionalidades Profissionais

- ✅ **Persistência em PostgreSQL**: Saída do SQLite para um banco pronto para múltiplos acessos concorrentes.
- ✅ **Segurança de Auditoria**: Tabela de `AuditLog` para rastrear ações críticas de usuários.
- ✅ **Rate Limiting**: Limite de 5 tentativas de login por minuto para evitar invasões.
- ✅ **PWA**: Pode ser instalado como aplicativo no Android/iOS.
- ✅ **Performance**: Bundles separados por rota para carregamento instantâneo.
- ✅ **Ambiente de Testes**: Suíte configurada com banco de dados em memória para validação contínua.

## 🛠️ Setup Rápido (Docker)

```bash
# 1. Suba a infraestrutura (Postgres + App)
docker-compose up -d

# 2. Migre seus dados do SQLite para o Postgres (Opcional se já tiver dados)
# Certifique-se que o arquivo mercado.db está na raiz do backend
docker-compose exec backend python scripts/migrate_sqlite_to_postgres.py

# 3. Acesse
# Frontend: http://localhost:5173
# API Docs: http://localhost:8007/docs
```

## 🧪 Executando Testes

```bash
cd backend
pytest
```

## 🔒 Segurança de Dados

- **Criptografia**: Senhas protegidas com **Bcrypt** (salting automático).
- **Autenticação**: JWT com expiração de 24h.
- **Isolamento**: Fiscais só acessam cessionários vinculados a eles (via query filtering).
- **Rate Limit**: Proteção ativa no endpoint de login via IP.

## 📄 Licença

Sistema desenvolvido para o Mercado Público de Solânea - PB.

---
**Desenvolvido com:** Python + React + Docker + PostgreSQL
**Melhorias e Modernização:** Antigravity AI Assistance (Google Deepmind)

