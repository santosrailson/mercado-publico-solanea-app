# Backend - Mercado Público API

FastAPI backend para o sistema de gestão do Mercado Público.

## Estrutura

```
app/
├── api/          # Rotas e endpoints
├── core/         # Configurações e segurança
├── crud/         # Operações CRUD
├── db/           # Database e sessões
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
└── services/     # Serviços auxiliares (PDF, Excel)
```

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker-compose up backend
```
