#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Garantir que importações da app funcionem
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

def migrate_data():
    sqlite_url = "sqlite:///../mercado.db"
    pg_url = "postgresql://mercado:mercado123@localhost:5432/mercado"

    print(f"🔄 Conectando ao SQLite: {sqlite_url}")
    sqlite_engine = create_engine(sqlite_url)
    
    print(f"🔄 Conectando ao PostgreSQL: {pg_url}")
    try:
        pg_engine = create_engine(pg_url)
        # Test connection
        with pg_engine.connect() as conn:
            pass
    except Exception as e:
        print(f"❌ Erro ao conectar no PostgreSQL: {e}")
        print("Certifique-se de que o Docker está rodando e executou: docker-compose up -d db")
        sys.exit(1)

    # Reflect tables
    sqlite_meta = MetaData()
    sqlite_meta.reflect(bind=sqlite_engine)
    
    pg_meta = MetaData()
    pg_meta.reflect(bind=pg_engine)

    if not pg_meta.tables:
        print("❌ Tabelas não encontradas no PostgreSQL.")
        print("Execute 'alembic upgrade head' antes de rodar este script.")
        sys.exit(1)

    # Definir ordem de tabelas para respeitar Foreign Keys
    tables_order = [
        "fiscais",
        "users",
        "cessionarios",
        "pagamentos",
        "certidoes",
        "audit_logs"
    ]

    sqlite_session = sessionmaker(bind=sqlite_engine)()
    pg_session = sessionmaker(bind=pg_engine)()

    try:
        for table_name in tables_order:
            if table_name not in sqlite_meta.tables:
                continue
                
            sqlite_table = sqlite_meta.tables[table_name]
            pg_table = pg_meta.tables[table_name]
            
            # Read all rows from sqlite
            rows = sqlite_engine.execute(sqlite_table.select()).fetchall()
            if not rows:
                print(f"Tabela {table_name}: vazia.")
                continue
                
            print(f"Migrando tabela {table_name}: {len(rows)} registros...")
            
            # Delete existing rows in postgres to avoid conflict
            pg_engine.execute(pg_table.delete())
            
            # Insert into postgres
            dicts = [dict(row) for row in rows]
            pg_engine.execute(pg_table.insert(), dicts)
            
            # Reset sequence for postgres if id exists
            if 'id' in pg_table.c:
                seq_name = f"{table_name}_id_seq"
                try:
                    pg_engine.execute(f"SELECT setval('{seq_name}', (SELECT MAX(id) FROM {table_name}));")
                except:
                    pass
        
        print("✅ Migração de dados concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
    finally:
        sqlite_session.close()
        pg_session.close()

if __name__ == "__main__":
    migrate_data()
