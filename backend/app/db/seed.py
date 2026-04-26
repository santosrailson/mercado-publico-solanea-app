"""
Script para criar dados iniciais no banco.
Execute: python -m app.db.seed
"""

import os
from datetime import datetime

from app.db.database import SessionLocal, engine
from app.models.models import Base, User, UserRole, UserStatus, Cessionario
from app.core.security import get_password_hash


def parse_valor(valor_str):
    """Converte 'R$ 15,00' ou 'R$ 1.234,56' para float"""
    limpo = valor_str.replace('R$', '').strip()
    limpo = limpo.replace('.', '').replace(',', '.')
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def importar_cessionarios_do_txt(db):
    """Importa cessionários de arquivo texto se o banco estiver vazio."""
    possiveis_caminhos = [
        "/app/cessionarios_pdf.txt",
        "/app/scripts/cessionarios_pdf.txt",
        "./cessionarios_pdf.txt",
        "./scripts/cessionarios_pdf.txt",
    ]

    caminho_txt = None
    for p in possiveis_caminhos:
        if os.path.exists(p):
            caminho_txt = p
            break

    if not caminho_txt:
        return False

    # Verifica se já existem cessionários
    total = db.query(Cessionario).count()
    if total > 0:
        print(f"ℹ️ Já existem {total} cessionários no banco — pulando importação automática")
        return False

    with open(caminho_txt, 'r', encoding='utf-8') as f:
        linhas = [l.strip() for l in f.readlines()]

    ignorar = {
        'Lista de Cessionários', 'Nome', 'Box/Ponto', 'Atividade',
        'Situação', 'Valor Ref.', 'Resumo:', ''
    }
    linhas = [
        l for l in linhas
        if l not in ignorar
        and not l.startswith('Emitido em:')
        and not l.startswith('Total:')
        and not l.startswith('Regulares:')
        and not l.startswith('Irregulares:')
        and not l.startswith('Total')
    ]

    cessionarios = []
    i = 0
    while i < len(linhas):
        nome = linhas[i]
        if nome.startswith('R$'):
            i += 1
            continue
        if nome == 'Resumo:':
            break
        if i + 1 >= len(linhas):
            break

        box = linhas[i + 1]
        if box.startswith('R$'):
            i += 1
            continue

        if i + 2 >= len(linhas):
            break
        atividade = linhas[i + 2]

        j = 3
        if atividade.startswith('R$'):
            atividade = ''
            j = 2
        elif atividade in ('Regular', 'Irregular'):
            atividade = ''
            j = 2

        if i + j >= len(linhas):
            break
        situacao = linhas[i + j]
        if situacao.startswith('R$'):
            situacao = 'Regular'
        else:
            j += 1

        if i + j >= len(linhas):
            break
        valor_str = linhas[i + j]

        if not valor_str.startswith('R$'):
            if 'R$' in valor_str:
                partes = valor_str.split('R$')
                if len(partes) >= 2 and partes[0].strip() in ('Regular', 'Irregular'):
                    situacao = partes[0].strip()
                    valor_str = 'R$' + partes[1].strip()
                else:
                    if i + j + 1 < len(linhas) and linhas[i + j + 1].startswith('R$'):
                        valor_str = linhas[i + j + 1]
                        j += 1
                    else:
                        valor_str = 'R$ 0,00'
            else:
                if i + j + 1 < len(linhas) and linhas[i + j + 1].startswith('R$'):
                    valor_str = linhas[i + j + 1]
                    j += 1
                else:
                    valor_str = 'R$ 0,00'

        i += j + 1

        nome = nome.strip()
        box = box.strip() if box and box != '-' else None
        atividade = atividade.strip() if atividade else None
        situacao = situacao.strip() if situacao in ('Regular', 'Irregular') else 'Regular'
        valor = parse_valor(valor_str)

        if nome and len(nome) > 2 and nome not in ('Regular', 'Irregular', 'Resumo:'):
            cessionarios.append({
                'nome': nome,
                'numero_box': box,
                'atividade': atividade,
                'situacao': situacao,
                'valor_referencia': valor,
            })

    if not cessionarios:
        return False

    situacao_map = {'Regular': 'REGULAR', 'Irregular': 'IRREGULAR'}
    agora = datetime.utcnow()

    for c in cessionarios:
        db_cessionario = Cessionario(
            nome=c['nome'],
            numero_box=c['numero_box'],
            atividade=c['atividade'],
            situacao=situacao_map.get(c['situacao'], 'REGULAR'),
            valor_referencia=c['valor_referencia'],
            periodicidade_referencia='MENSAL',
            created_at=agora,
            updated_at=agora,
        )
        db.add(db_cessionario)

    db.commit()
    print(f"✅ {len(cessionarios)} cessionários importados automaticamente de {caminho_txt}")
    return True


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Verifica se já existe usuário admin
        admin = db.query(User).filter(User.email == "admin@mercado.pb.gov.br").first()

        if not admin:
            admin = User(
                nome="Administrador",
                email="admin@mercado.pb.gov.br",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            db.add(admin)
            db.commit()
            print("✅ Usuário admin criado:")
            print("   Email: admin@mercado.pb.gov.br")
            print("   Senha: admin123")
        else:
            print("ℹ️ Usuário admin já existe")

        # Importa cessionários automaticamente se o banco estiver vazio
        importar_cessionarios_do_txt(db)

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
