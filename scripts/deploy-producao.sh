#!/bin/bash
set -e

# =============================================================================
# Script de Deploy para Produção: SQLite → PostgreSQL
# Execute este script no VPS Hostinger via SSH
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DEPLOY: SQLite → PostgreSQL${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# PASSO 1: Backup do SQLite atual
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/6] Fazendo backup do banco SQLite atual...${NC}"
BACKUP_FILE="mercado-producao-backup-$(date +%Y%m%d-%H%M%S).db"

if docker ps | grep -q mercado-backend; then
    echo "   Container backend encontrado. Copiando banco..."
    docker cp mercado-backend:/app/data/mercado.db ./$BACKUP_FILE
    echo -e "   ${GREEN}✅ Backup criado: $BACKUP_FILE${NC}"
else
    echo -e "   ${RED}❌ Container mercado-backend não encontrado rodando!${NC}"
    echo "   Verificando containers parados..."
    docker ps -a | grep mercado-backend || true
    
    read -p "Deseja tentar copiar de um container parado? (s/n): " resposta
    if [ "$resposta" = "s" ]; then
        docker cp mercado-backend:/app/data/mercado.db ./$BACKUP_FILE
        echo -e "   ${GREEN}✅ Backup criado do container parado: $BACKUP_FILE${NC}"
    else
        echo -e "   ${RED}❌ Deploy cancelado. Não foi possível fazer backup.${NC}"
        exit 1
    fi
fi

echo ""

# -----------------------------------------------------------------------------
# PASSO 2: Parar os containers antigos
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/6] Parando containers antigos (SQLite)...${NC}"
docker-compose down
echo -e "   ${GREEN}✅ Containers antigos parados${NC}"
echo ""

# -----------------------------------------------------------------------------
# PASSO 3: Subir apenas o PostgreSQL
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/6] Subindo PostgreSQL...${NC}"
docker-compose up -d db

# Aguardar PostgreSQL ficar pronto
echo "   Aguardando PostgreSQL iniciar..."
sleep 5
for i in {1..30}; do
    if docker exec mercado-db pg_isready -U mercado -d mercado > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ PostgreSQL pronto!${NC}"
        break
    fi
    echo "   Tentativa $i/30..."
    sleep 2
done

echo ""

# -----------------------------------------------------------------------------
# PASSO 4: Migrar dados do SQLite para PostgreSQL
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/6] Migrando dados do SQLite para PostgreSQL...${NC}"

# Criar script Python temporário para migração
cat > /tmp/migrar_dados.py << 'PYEOF'
import sys
import os
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SQLITE_PATH = sys.argv[1] if len(sys.argv) > 1 else "./mercado-producao-backup.db"
PG_URL = os.environ.get("DATABASE_URL", "postgresql://mercado:mercado123@localhost:5432/mercado")

TABLES_ORDER = ['fiscais', 'users', 'cessionarios', 'pagamentos', 'certidoes']

def get_sqlite_data(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    data = {}
    for table in TABLES_ORDER:
        cursor.execute(f"SELECT * FROM {table}")
        rows = [dict(row) for row in cursor.fetchall()]
        data[table] = rows
        print(f"  📖 {table}: {len(rows)} registros")
    conn.close()
    return data

def get_boolean_columns(pg_engine, table_name):
    with pg_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = :table AND data_type = 'boolean'
        """), {"table": table_name})
        return [row[0] for row in result]

def convert_value(value, col_name, boolean_cols):
    if col_name in boolean_cols:
        return bool(value) if value is not None else None
    if isinstance(value, str) and value:
        if col_name in ('created_at', 'updated_at', 'data_pagamento', 'data_emissao', 'data_referencia', 'data_validade'):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
    return value

def reset_sequences(pg_session):
    for table in TABLES_ORDER:
        pg_session.execute(text(f"""
            SELECT setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)
        """))
    pg_session.commit()

def migrate():
    print(f"📂 SQLite: {SQLITE_PATH}")
    sqlite_data = get_sqlite_data(SQLITE_PATH)
    
    print(f"\n🐘 PostgreSQL: {PG_URL}")
    engine = create_engine(PG_URL)
    Session = sessionmaker(bind=engine)
    pg_session = Session()
    
    table_boolean_cols = {}
    for table in TABLES_ORDER:
        table_boolean_cols[table] = get_boolean_columns(engine, table)
    
    try:
        pg_session.execute(text("SET session_replication_role = 'replica';"))
        total = 0
        
        for table in TABLES_ORDER:
            rows = sqlite_data[table]
            if not rows:
                print(f"  ⏭️  {table}: vazio")
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
                total += 1
            
            print(f"  ✅ {table}: {len(rows)} registros inseridos")
        
        pg_session.execute(text("SET session_replication_role = 'origin';"))
        pg_session.commit()
        reset_sequences(pg_session)
        
        print(f"\n🎉 Total migrado: {total} registros")
        
    except Exception as e:
        pg_session.rollback()
        print(f"\n❌ Erro: {e}")
        raise
    finally:
        pg_session.close()

if __name__ == '__main__':
    migrate()
PYEOF

# Executar migração dentro do container backend (que tem Python + dependências)
# Primeiro, precisamos buildar o backend com as novas dependências
echo "   Buildando backend com PostgreSQL support..."
docker-compose build backend > /dev/null 2>&1

# Executar o script de migração usando o container backend
# Montando o backup no container temporariamente
docker run --rm \
    -v $(pwd)/$BACKUP_FILE:/tmp/backup.db \
    -e DATABASE_URL=postgresql://mercado:mercado123@db:5432/mercado \
    --network mercado-publico-solanea-app_mercado-network \
    mercado-publico-solanea-app-backend:latest \
    python -c "
import sys
sys.path.insert(0, '/app')
exec(open('/tmp/migrar_dados.py').read())
" /tmp/backup.db

# Se falhar, tentar rodar localmente com python3
if [ $? -ne 0 ]; then
    echo "   Tentando migração local..."
    pip install psycopg2-binary sqlalchemy > /dev/null 2>&1 || true
    DATABASE_URL=postgresql://mercado:mercado123@localhost:5432/mercado python3 /tmp/migrar_dados.py ./$BACKUP_FILE
fi

echo ""

# -----------------------------------------------------------------------------
# PASSO 5: Subir a aplicação completa
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/6] Subindo aplicação completa (backend + frontend)...${NC}"
docker-compose up -d --build
echo -e "   ${GREEN}✅ Aplicação no ar!${NC}"
echo ""

# -----------------------------------------------------------------------------
# PASSO 6: Validação
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[6/6] Validando deploy...${NC}"
sleep 5

# Verificar se backend está respondendo
if curl -s http://localhost:8007/health > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Backend respondendo${NC}"
else
    echo -e "   ${RED}⚠️  Backend não respondeu ainda (pode levar alguns segundos)${NC}"
fi

# Verificar contagem de cessionários
CESSIONARIOS=$(docker exec mercado-db psql -U mercado -d mercado -t -c "SELECT COUNT(*) FROM cessionarios;" 2>/dev/null | xargs)
echo -e "   ${GREEN}✅ Cessionários no PostgreSQL: $CESSIONARIOS${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DEPLOY CONCLUÍDO!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Backup salvo em: $BACKUP_FILE"
echo ""
echo "Para verificar logs:"
echo "  docker logs -f mercado-backend"
echo ""
echo "Para verificar o banco:"
echo "  docker exec -it mercado-db psql -U mercado -d mercado"
