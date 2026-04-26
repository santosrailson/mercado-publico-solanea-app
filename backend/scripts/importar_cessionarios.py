#!/usr/bin/env python3
"""
Script para importar cessionários de um arquivo texto extraído de PDF
para o banco SQLite do sistema.

Uso:
    python importar_cessionarios.py <arquivo_txt> <caminho_banco_sqlite>

Exemplo:
    python importar_cessionarios.py cessionarios.txt ./data/mercado.db
"""

import sys
import sqlite3
from datetime import datetime


def parse_valor(valor_str):
    """Converte 'R$ 15,00' ou 'R$ 1.234,56' para float"""
    limpo = valor_str.replace('R$', '').strip()
    limpo = limpo.replace('.', '').replace(',', '.')
    try:
        return float(limpo)
    except ValueError:
        return 0.0


def importar_cessionarios(arquivo_txt, db_path):
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
        # SQLAlchemy SQLite Enum armazena os NOMES dos membros em maiúsculo
        situacao_map = {'Regular': 'REGULAR', 'Irregular': 'IRREGULAR'}
        situacao = situacao_map.get(situacao.strip(), 'REGULAR')
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

    # Conecta ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='cessionarios'"
    )
    if not cursor.fetchone():
        print("ERRO: Tabela 'cessionarios' não encontrada no banco!")
        conn.close()
        sys.exit(1)

    inseridos = 0
    duplicados = 0
    agora = datetime.utcnow().isoformat()

    for c in cessionarios:
        cursor.execute("SELECT id FROM cessionarios WHERE nome = ?", (c['nome'],))
        if cursor.fetchone():
            print(f"  ⚠️  Já existe: {c['nome']} — pulando")
            duplicados += 1
            continue

        cursor.execute("""
            INSERT INTO cessionarios
            (nome, numero_box, atividade, situacao, valor_referencia,
             periodicidade_referencia, observacoes, fiscal_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c['nome'],
            c['numero_box'],
            c['atividade'],
            c['situacao'],
            c['valor_referencia'],
            'MENSAL',
            None,
            None,
            agora,
            agora
        ))
        inseridos += 1
        print(f"  ✅ Inserido: {c['nome']}")

    conn.commit()
    conn.close()

    print(f"\n{'='*50}")
    print(f"Resumo da importação:")
    print(f"  Encontrados no arquivo: {len(cessionarios)}")
    print(f"  Inseridos: {inseridos}")
    print(f"  Duplicados (pulados): {duplicados}")
    print(f"{'='*50}")
    print(f"\nPróximos passos:")
    print(f"  1. Acesse a tela de Cessionários para atualizar telefones")
    print(f"  2. Cadastre os Fiscais e vincule aos cessionários")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python importar_cessionarios.py <arquivo_txt> <caminho_banco_sqlite>")
        sys.exit(1)

    importar_cessionarios(sys.argv[1], sys.argv[2])
