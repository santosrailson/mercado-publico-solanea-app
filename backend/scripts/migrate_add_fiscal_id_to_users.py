"""
Script de migração: adiciona coluna fiscal_id à tabela users.
Execute dentro do container backend:
    python scripts/migrate_add_fiscal_id_to_users.py
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
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "fiscal_id" in columns:
        print("ℹ️  Coluna fiscal_id já existe na tabela users")
    else:
        cursor.execute("ALTER TABLE users ADD COLUMN fiscal_id INTEGER REFERENCES fiscais(id)")
        conn.commit()
        print("✅ Coluna fiscal_id adicionada à tabela users")
    
    conn.close()

if __name__ == "__main__":
    migrate()
