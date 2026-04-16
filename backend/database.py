import os
import aiosqlite
from contextlib import asynccontextmanager

DB_PATH = os.getenv("DB_PATH", "/data/mercado.db")

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    aprovado INTEGER NOT NULL DEFAULT 1,
    criado_por TEXT,
    criado_em TEXT
);
"""

CREATE_CESSIONARIOS = """
CREATE TABLE IF NOT EXISTS cessionarios (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    numero_box TEXT,
    atividade TEXT,
    telefone TEXT,
    situacao TEXT NOT NULL DEFAULT 'Regular',
    valor_ref REAL NOT NULL DEFAULT 0,
    per_ref TEXT DEFAULT 'Mensal',
    observacao TEXT,
    criado_por TEXT,
    criado_em TEXT
);
"""

CREATE_PAGAMENTOS = """
CREATE TABLE IF NOT EXISTS pagamentos (
    id TEXT PRIMARY KEY,
    cessionario_id TEXT NOT NULL,
    data TEXT NOT NULL,
    valor REAL NOT NULL,
    periodicidade TEXT NOT NULL DEFAULT 'Mensal',
    observacao TEXT,
    usuario_id TEXT,
    criado_em TEXT,
    FOREIGN KEY (cessionario_id) REFERENCES cessionarios(id)
);
"""


@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


async def init_db():
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys=ON")
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_CESSIONARIOS)
        await db.execute(CREATE_PAGAMENTOS)
        await db.commit()

        # Check if users exist
        async with db.execute("SELECT COUNT(*) as c FROM users") as cursor:
            row = await cursor.fetchone()
            if row["c"] == 0:
                from seed import run_seed
                await run_seed(db)
