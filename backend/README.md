# Backend - Mercado Público API (Professional Edition)

FastAPI backend robusto para o sistema de gestão do Mercado Público de Solânea - PB.

## 🛠️ Tecnologias e Segurança
- **FastAPI**: Performance assíncrona.
- **PostgreSQL**: Banco de dados de produção.
- **Alembic**: Versionamento de esquema.
- **Bcrypt**: Criptografia de senhas (Passlib).
- **SlowAPI**: Rate limiting no login (Anti Brute-force).
- **JWT**: Autenticação stateless.

## 📂 Estrutura de Pastas
```
app/
├── api/          # Endpoints (Dashboard, Fiscais, etc.)
├── core/         # Configuração central, Security e Rate Limit
├── crud/         # Camada de persistência
├── db/           # Session setup e Seed data
├── models/       # Modelos SQLAlchemy (AuditLog incluso)
├── schemas/      # Modelos Pydantic para validação
└── services/     # Serviços de PDF e Excel
alembic/          # Scripts de migração de banco
tests/            # Suíte de testes com Pytest
```

## 🚀 Como Rodar Localmente

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis
Copie o `.env.example` para `.env` e ajuste a `DATABASE_URL` (padrão Postgres).

### 3. Migrações
```bash
alembic upgrade head
```

### 4. Iniciar Servidor
```bash
uvicorn app.main:app --reload --port 8007
```

## 🧪 Testes
Para rodar a suíte de testes (utiliza banco in-memory isolado):
```bash
pytest
```

## 🔄 Migração de Dados
Se você estiver saindo do SQLite antigo para o PostgreSQL novo, use nosso script de migração:
```bash
python scripts/migrate_sqlite_to_postgres.py
```
