#!/usr/bin/env python3
"""
Script para importar cessionários de um arquivo texto extraído de PDF.

Uso:
    python importar_cessionarios.py <arquivo_txt>

Exemplo:
    python importar_cessionarios.py cessionarios.txt
"""

import sys
import os
from datetime import datetime

# Adiciona o path para importar os módulos do app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal
from app.models.models import Cessionario, SituacaoCessionario, Periodicidade


def parse_valor(valor_str):
    """Converte 'R$ 15,00' ou 'R$ 1.234,56' para float"""
    limpo = valor_str.replace('R$', '').strip()
    limpo = limpo.replace('.', '').replace(',', '.')
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def importar_cessionarios(arquivo_txt):
    with open(arquivo_txt, 'r', encoding='utf-8') as f:
        linhas = [l.strip() for l in f.readlines()]

    # Remove linhas vazias e cabeçalhos conhecidos
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

        # Pula valores soltos (erros de parsing)
        if nome.startswith('R$'):
            i += 1
            continue

        # Fim do documento
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

        # Detecta se atividade está faltando (próxima é situação ou valor)
        j = 3
        if atividade.startswith('R$'):
            atividade = ''
            j = 2
        elif atividade in ('Regular', 'Irregular'):
            # Faltou atividade, essa linha é a situação
            atividade = ''
            j = 2

        if i + j >= len(linhas):
            break
        situacao = linhas[i + j]

        if situacao.startswith('R$'):
            # Faltou situação, essa linha é o valor
            situacao = 'Regular'
        else:
            j += 1

        if i + j >= len(linhas):
            break
        valor_str = linhas[i + j]

        # Tenta corrigir se situação e valor estiverem juntos
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
        situacao_map = {'Regular': SituacaoCessionario.REGULAR, 'Irregular': SituacaoCessionario.IRREGULAR}
        situacao = situacao_map.get(situacao.strip(), SituacaoCessionario.REGULAR)
        valor = parse_valor(valor_str)

        if nome and len(nome) > 2 and nome not in ('Regular', 'Irregular', 'Resumo:'):
            cessionarios.append({
                'nome': nome,
                'numero_box': box,
                'atividade': atividade,
                'situacao': situacao,
                'valor_referencia': valor,
            })

    print(f"Total de cessionários encontrados no arquivo: {len(cessionarios)}")

    db = SessionLocal()
    try:
        inseridos = 0
        duplicados = 0
        agora = datetime.utcnow()

        for c in cessionarios:
            existe = db.query(Cessionario).filter(Cessionario.nome == c['nome']).first()
            if existe:
                print(f"  ⚠️  Já existe: {c['nome']} — pulando")
                duplicados += 1
                continue

            novo = Cessionario(
                nome=c['nome'],
                numero_box=c['numero_box'],
                atividade=c['atividade'],
                situacao=c['situacao'],
                valor_referencia=c['valor_referencia'],
                periodicidade_referencia=Periodicidade.MENSAL,
                observacoes=None,
                fiscal_id=None,
                created_at=agora,
                updated_at=agora,
            )
            db.add(novo)
            inseridos += 1
            print(f"  ✅ Inserido: {c['nome']}")

        db.commit()

        print(f"\n{'='*50}")
        print(f"Resumo da importação:")
        print(f"  Encontrados no arquivo: {len(cessionarios)}")
        print(f"  Inseridos: {inseridos}")
        print(f"  Duplicados (pulados): {duplicados}")
        print(f"{'='*50}")
        print(f"\nPróximos passos:")
        print(f"  1. Acesse a tela de Cessionários para atualizar telefones")
        print(f"  2. Cadastre os Fiscais e vincule aos cessionários")

    finally:
        db.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python importar_cessionarios.py <arquivo_txt>")
        sys.exit(1)

    importar_cessionarios(sys.argv[1])
