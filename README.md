# Mercado Público - Sistema de Gestão

Sistema moderno de gestão para o Mercado Público de Solânea - PB.

Arquitetura separada em backend (Python/FastAPI) e frontend (React/TypeScript), containerizada com Docker.

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
│   ├── scripts/         # Scripts utilitários
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

### Gestão de Cessionários
- ✅ Cadastro, edição e exclusão de cessionários/feirantes
- ✅ Filtros por nome, box, situação e fiscal responsável
- ✅ Auto-preenchimento de valores ao registrar pagamentos
- ✅ Vinculação com fiscal responsável

### Controle de Pagamentos
- ✅ Registro de pagamentos com periodicidade
- ✅ Compartilhamento via WhatsApp
- ✅ Histórico completo por cessionário

### Gestão de Fiscais
- ✅ Cadastro de fiscais com dados pessoais
- ✅ Vinculação de usuários do sistema aos fiscais
- ✅ **Fiscal logado só visualiza e gerencia seus próprios cessionários**

### Relatórios
- ✅ Relatório geral de cessionários (PDF/Excel)
- ✅ Cessionários regulares e irregulares
- ✅ Arrecadação por período
- ✅ Relatório de cobrança com recibos
- ✅ Certidões de situação com código de verificação
- ✅ Filtro por fiscal em todos os relatórios

### Usuários e Autenticação
- ✅ Login com JWT
- ✅ Papéis: Administrador, Operador, Visualizador
- ✅ Gestão completa de usuários (admin)
- ✅ Aprovação de usuários pendentes
- ✅ **Perfil do usuário** - edição de nome/email
- ✅ **Alteração de senha** pelo próprio usuário

### Dashboard
- ✅ KPIs: total, regulares, irregulares, arrecadação
- ✅ Gráfico de arrecadação mensal
- ✅ Gráfico de situação (pizza)
- ✅ Top cessionários
- ✅ Atividades recentes
- ✅ **Filtragem automática por fiscal logado**

### Outros
- ✅ Temas claro/escuro
- ✅ Design responsivo
- ✅ Verificação pública de certidões

## 🛠️ Setup

### Via Docker (Recomendado)

```bash
# Clone o repositório
git clone <repo-url>
cd mercado-publico

# Suba os containers
docker-compose up -d

# Acesse
# Frontend: http://localhost:8080
# API Docs: http://localhost:8007/docs
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

O sistema cria automaticamente um usuário admin na primeira execução:

- **Email**: `admin@mercado.pb.gov.br`
- **Senha**: `admin123`

Após o primeiro login:
1. Cadastre os fiscais em **Fiscais**
2. Crie os usuários em **Usuários** e vincule-os aos fiscais
3. Os fiscais poderão logar e gerenciar apenas seus cessionários

> ⚠️ **Importante**: O vínculo entre usuário e fiscal é feito pelo campo "Fiscal vinculado" na tela de usuários.

## 🗄️ Migração de Banco de Dados

Ao adicionar novas colunas/tabelas (sem Alembic ativo), use os scripts de migração:

```bash
# Adicionar coluna fiscal_id na tabela users (após atualização)
docker compose run --rm backend python scripts/migrate_add_fiscal_id_to_users.py
```

> 💡 O script detecta se a coluna já existe e não duplica.

## 🆘 Recuperação de Acesso

Se o admin perder o acesso (status alterado, senha perdida, etc.):

```bash
docker compose run --rm backend python scripts/recuperar_admin.py
```

Isso redefine o admin para:
- Email: `admin@mercado.pb.gov.br`
- Senha: `admin123`
- Status: Ativo
- Role: Administrador

## 📚 Documentação da API

Com o backend rodando, acesse:
- Swagger UI: `http://localhost:8007/docs`
- ReDoc: `http://localhost:8007/redoc`

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

| Tabela | Descrição |
|--------|-----------|
| **users** | Usuários do sistema (login) |
| **fiscais** | Fiscais do mercado |
| **cessionarios** | Cessionários e feirantes |
| **pagamentos** | Registro de pagamentos |
| **certidoes** | Certidões emitidas |

### Relacionamentos principais
- `users.fiscal_id` → `fiscais.id` (vínculo usuário-fiscal)
- `cessionarios.fiscal_id` → `fiscais.id` (cessionário do fiscal)
- `pagamentos.cessionario_id` → `cessionarios.id`

## 🎨 Design System

- Cores primárias: Verde-água (#00c896)
- Tema escuro: Azul-marinho (#07111e)
- Tipografia: Inter
- Componentes reutilizáveis em `frontend/src/components/ui/`

## 🔒 Segurança

- Autenticação JWT com expiração
- Senhas hasheadas com pbkdf2_sha256
- CORS configurado
- SQL injection protegido via ORM
- XSS protegido via React
- **Fiscais só acessam seus próprios dados** (filtro automático em todas as APIs)
- **Ownership check**: fiscal não pode editar/excluir cessionários de outros fiscais

## 🚀 Deploy

### Produção com Docker (Hostinger/VPS)

```bash
# 1. Faça pull no servidor
ssh root@seu-servidor
cd ~/mercado-publico-solanea-app
git pull

# 2. Migração (se necessário)
docker compose run --rm backend python scripts/migrate_add_fiscal_id_to_users.py

# 3. Build e restart (NUNCA use down -v)
docker compose build && docker compose up -d
```

> ⚠️ **ATENÇÃO**: `docker compose down -v` apaga o volume do SQLite e **todos os dados**! Sempre use `up -d` para manter os dados.

### Variáveis de Ambiente

```env
# Backend
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=["https://seudominio.com"]

# Frontend
VITE_API_URL=https://api.seudominio.com
```

## 📄 Licença

Sistema desenvolvido para o Mercado Público de Solânea - PB.

---

**Desenvolvido com:** Python + React + Docker

**Melhorias profissionais (FastAPI + React):** Implementadas com auxílio do Kimi 2.5
