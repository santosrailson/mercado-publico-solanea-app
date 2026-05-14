# Backend – Mercado Público API (Professional Edition)

FastAPI backend robusto para o sistema de gestão do Mercado Público de Solânea - PB.

## 📚 Visão Geral
Este repositório contém a API RESTful que fornece:
- Gerenciamento de cessionários, pagamentos e fiscais.
- Autenticação baseada em JWT com suporte a múltiplos papéis (Admin, Operador, Visualizador).
- Auditoria de ações críticas via `AuditLog`.
- Proteção contra força‑bruta com **SlowAPI**.

## 🛠️ Tecnologias e Segurança
- **FastAPI** – Performance assíncrona.
- **PostgreSQL** – Banco de dados de produção.
- **Alembic** – Versionamento de esquema.
- **SQLAlchemy 2.0** – ORM.
- **Passlib (Bcrypt)** – Hash de senhas.
- **SlowAPI** – Rate limiting no endpoint de login.
- **JWT** – Autenticação stateless.

## 📂 Estrutura de Pastas
```
app/
├── api/          # Endpoints (Dashboard, Fiscais, etc.)
├── core/         # Configurações centralizadas (Security, Rate Limit)
├── crud/         # Operações de persistência
├── db/           # Session e seed data
├── models/       # Modelos SQLAlchemy (inclui AuditLog)
├── schemas/      # Schemas Pydantic para validação
└── services/     # Serviços auxiliares (PDF, Excel)

alembic/          # Scripts de migração de banco
tests/            # Suíte de testes com Pytest
```

## 🚀 Como Rodar Localmente

### 1️⃣ Instalar dependências
```bash
pip install -r requirements.txt
```

### 2️⃣ Configurar variáveis de ambiente
Copie o arquivo de exemplo e ajuste a URL do banco:
```bash
cp .env.example .env
# Edite .env se necessário – DATABASE_URL já aponta para o container PostgreSQL
```

### 3️⃣ Executar migrações
```bash
alembic upgrade head
```

### 4️⃣ Iniciar o servidor
```bash
uvicorn app.main:app --reload --port 8007
```
A API ficará disponível em `http://localhost:8007/`. A documentação Swagger está em `http://localhost:8007/docs`.

## 🧪 Testes
A suíte de testes utiliza um banco SQLite em memória para garantir isolamento.
```bash
pytest
```

## 🔄 Migração de Dados (SQLite → PostgreSQL)
Caso ainda possua o banco SQLite antigo, use o script de migração:
```bash
python scripts/migrate_sqlite_to_postgres.py
```

## 📦 Docker (opcional)
Para rodar tudo em containers:
```bash
docker-compose up -d
```
O serviço `backend` será exposto na porta **8007**.

## 🤝 Contribuição
1. Fork o repositório.
2. Crie uma branch (`git checkout -b feature/...`).
3. Submeta um Pull Request descrevendo a mudança.

## 📄 Licença
Este projeto está licenciado sob a licença **MIT**.
