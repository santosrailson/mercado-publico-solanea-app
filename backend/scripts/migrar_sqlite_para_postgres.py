#!/usr/bin/env python3
"""
Script para migrar dados do SQLite para PostgreSQL.

Uso:
    python scripts/migrar_sqlite_para_postgres.py <caminho_sqlite>

Exemplo:
    python scripts/migrar_sqlite_para_postgres.py ../mercado-backup-2026-04-29.db
"""

import sys
import os
from datetime import datetime

# Adiciona o path para importar os módulos do app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sqlite3
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings


SETTINGS = get_settings()
TABLES_ORDER = ['fiscais', 'users', 'cessionarios', 'pagamentos', 'certidoes']
SEQUENCE_TABLES = ['fiscais', 'users', 'cessionarios', 'pagamentos', 'certidoes']

# Colunas conhecidas como booleanas no schema
BOOLEAN_COLUMNS = {
    'fiscais': ['ativo'],
}


def get_sqlite_data(db_path):
    """Lê todos os dados do SQLite."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    data = {}
    for table in TABLES_ORDER:
        cursor.execute(f"SELECT * FROM {table}")
        rows = [dict(row) for row in cursor.fetchall()]
        data[table] = rows
        print(f"  📖 SQLite → {table}: {len(rows)} registros")

    conn.close()
    return data


def get_boolean_columns(pg_engine, table_name):
    """Descobre quais colunas são booleanas no PostgreSQL."""
    with pg_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table AND data_type = 'boolean'
        """), {"table": table_name})
        return [row[0] for row in result]


def convert_value(value, col_name, boolean_cols):
    """Converte valores do SQLite para o formato esperado pelo PostgreSQL."""
    if col_name in boolean_cols:
        if value is None:
            return None
        return bool(value)
    if isinstance(value, str) and value:
        # Tenta converter strings que parecem timestamps
        if col_name in ('created_at', 'updated_at', 'data_pagamento', 'data_emissao', 'data_referencia', 'data_validade'):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
    return value


def reset_sequences(pg_session):
    """Reseta as sequences do PostgreSQL para o maior ID + 1."""
    for table in SEQUENCE_TABLES:
        pg_session.execute(text(f"""
            SELECT setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)
        """))
    pg_session.commit()
    print("  🔄 Sequences resetadas")


def migrate_data(sqlite_db_path):
    if not os.path.exists(sqlite_db_path):
        print(f"❌ Banco SQLite não encontrado: {sqlite_db_path}")
        sys.exit(1)

    print(f"📂 Lendo dados do SQLite: {sqlite_db_path}")
    sqlite_data = get_sqlite_data(sqlite_db_path)

    print(f"\n🐘 Conectando ao PostgreSQL")
    engine = create_engine(SETTINGS.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    pg_session = Session()

    # Descobre colunas booleanas de cada tabela
    table_boolean_cols = {}
    for table in TABLES_ORDER:
        table_boolean_cols[table] = get_boolean_columns(engine, table)
        if table_boolean_cols[table]:
            print(f"  ℹ️  {table}: colunas booleanas = {table_boolean_cols[table]}")

    try:
        # Desabilita triggers de FK temporariamente para inserir fora de ordem
        pg_session.execute(text("SET session_replication_role = 'replica';"))

        total_inseridos = 0
        for table in TABLES_ORDER:
            rows = sqlite_data[table]
            if not rows:
                print(f"  ⏭️  {table}: vazio, pulando")
                continue

            columns = list(rows[0].keys())
            col_str = ', '.join(columns)
            placeholders = ', '.join([f':{c}' for c in columns])
            boolean_cols = table_boolean_cols.get(table, [])

            for row in rows:
                converted = {k: convert_value(v, k, boolean_cols) for k, v in row.items()}
                pg_session.execute(
                    text(f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"),
                    converted
                )
                total_inseridos += 1

            print(f"  ✅ {table}: {len(rows)} registros inseridos")

        # Reabilita triggers
        pg_session.execute(text("SET session_replication_role = 'origin';"))
        pg_session.commit()

        # Reseta sequences para evitar conflitos de PK em novos inserts
        reset_sequences(pg_session)

        print(f"\n{'='*50}")
        print(f"🎉 Migração concluída!")
        print(f"   Total de registros migrados: {total_inseridos}")
        print(f"{'='*50}")

    except Exception as e:
        pg_session.rollback()
        print(f"\n❌ Erro durante a migração: {e}")
        raise
    finally:
        pg_session.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        backup_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mercado-backup-2026-04-29.db')
        backup_path = os.path.abspath(backup_path)
        if os.path.exists(backup_path):
            print(f"📂 Backup encontrado automaticamente: {backup_path}")
            migrate_data(backup_path)
        else:
            print("Uso: python scripts/migrar_sqlite_para_postgres.py <caminho_sqlite>")
            sys.exit(1)
    else:
        migrate_data(sys.argv[1])
