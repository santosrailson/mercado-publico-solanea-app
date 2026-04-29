"""
Script de migração: adiciona coluna data_validade à tabela certidoes.
Execute dentro do container backend:
    python scripts/migrate_add_data_validade_to_certidoes.py
"""

import sqlite3
import os

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./app.db").replace("sqlite:///", "")


def migrate():
    if DB_PATH.startswith("/"):
        db_file = DB_PATH
    else:
        db_file = os.path.join(os.path.dirname(__file__), "..", DB_PATH)

    db_file = os.path.abspath(db_file)

    if not os.path.exists(db_file):
        print(f"❌ Banco de dados não encontrado: {db_file}")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Verifica se a coluna já existe
    cursor.execute("PRAGMA table_info(certidoes)")
    columns = [col[1] for col in cursor.fetchall()]

    if "data_validade" in columns:
        print("ℹ️  Coluna data_validade já existe na tabela certidoes")
    else:
        cursor.execute("ALTER TABLE certidoes ADD COLUMN data_validade DATETIME")
        conn.commit()
        print("✅ Coluna data_validade adicionada à tabela certidoes")

    conn.close()


if __name__ == "__main__":
    migrate()
