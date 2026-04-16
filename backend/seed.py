import uuid
from datetime import datetime, date, timedelta
from auth import hash_password


async def run_seed(db):
    now = datetime.utcnow().isoformat()

    # Admin user
    await db.execute(
        """INSERT OR IGNORE INTO users (id, nome, email, senha_hash, is_admin, aprovado, criado_por, criado_em)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            "admin_solanea_001",
            "Administrador",
            "admin@solanea.pb.gov.br",
            hash_password("admin123"),
            1,
            1,
            None,
            now,
        ),
    )

    # 20 cessionários representativos
    cessionarios = [
        ("Açougue do Zé",          "A-01", "Açougue",          "(83) 99100-0001", "Regular", 200.0),
        ("Padaria Solânea",         "A-02", "Padaria/Confeitaria","(83) 99100-0002", "Regular", 180.0),
        ("Hortifruti Sertão Verde", "A-03", "Hortifruti",       "(83) 99100-0003", "Regular", 150.0),
        ("Peixaria Mar Seco",       "A-04", "Peixaria",         "(83) 99100-0004", "Regular", 170.0),
        ("Mercearia Nordestina",    "B-01", "Mercearia",        "(83) 99100-0005", "Regular", 130.0),
        ("Armarinho da Dona Maria", "B-02", "Armarinho/Tecidos","(83) 99100-0006", "Regular", 120.0),
        ("Chaveiro e Elétrica",     "B-03", "Chaveiro",         "(83) 99100-0007", "Regular", 100.0),
        ("Farmácia Popular Box",    "B-04", "Farmácia",         "(83) 99100-0008", "Irregular", 250.0),
        ("Bazar da Esperança",      "C-01", "Bazar",            "(83) 99100-0009", "Regular", 110.0),
        ("Calçados Sertanejo",      "C-02", "Calçados",         "(83) 99100-0010", "Regular", 140.0),
        ("Lanchonete Sabor Bravo",  "C-03", "Lanchonete",       "(83) 99100-0011", "Regular", 160.0),
        ("Aviamentos e Costura",    "C-04", "Aviamentos",       "(83) 99100-0012", "Irregular", 90.0),
        ("Verduraria Fresca",       "D-01", "Verduraria",       "(83) 99100-0013", "Regular", 120.0),
        ("Temperos e Especiarias",  "D-02", "Temperos",         "(83) 99100-0014", "Regular", 80.0),
        ("Bijuterias e Acessórios", "D-03", "Bijuterias",       "(83) 99100-0015", "Regular", 100.0),
        ("Papelaria Estudante",     "D-04", "Papelaria",        "(83) 99100-0016", "Regular", 110.0),
        ("Sapateiro Remendão",      "E-01", "Sapateiro",        "(83) 99100-0017", "Irregular", 80.0),
        ("Relojoaria Precisa",      "E-02", "Relojoaria",       "(83) 99100-0018", "Regular", 90.0),
        ("Casa de Sucos Natural",   "E-03", "Sucos/Vitaminas",  "(83) 99100-0019", "Regular", 130.0),
        ("Empório Sertão Livre",    "E-04", "Empório",          "(83) 99100-0020", "Regular", 175.0),
    ]

    cess_ids = []
    for nome, box, atividade, tel, situacao, valor in cessionarios:
        cid = str(uuid.uuid4())
        cess_ids.append((cid, situacao, valor))
        await db.execute(
            """INSERT OR IGNORE INTO cessionarios
               (id, nome, numero_box, atividade, telefone, situacao, valor_ref, per_ref, criado_por, criado_em)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (cid, nome, box, atividade, tel, situacao, valor, "Mensal", "admin_solanea_001", now),
        )

    # Seed pagamentos — últimos 5 meses fechados para cessionários Regulares
    today = date.today()

    def mes_anterior(ano, mes, n):
        """Retorna (ano, mes) subtraindo n meses."""
        m = mes - n
        a = ano + (m - 1) // 12
        m = ((m - 1) % 12) + 1
        return a, m

    for cid, situacao, valor in cess_ids:
        if situacao != "Regular":
            continue
        for n in range(1, 6):  # 5 meses anteriores ao mês atual
            ano, mes = mes_anterior(today.year, today.month, n)
            pay_date = date(ano, mes, 5)
            pid = str(uuid.uuid4())
            await db.execute(
                """INSERT OR IGNORE INTO pagamentos
                   (id, cessionario_id, data, valor, periodicidade, usuario_id, criado_em)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (pid, cid, pay_date.isoformat(), valor, "Mensal", "admin_solanea_001", now),
            )

    await db.commit()
    print("[seed] Banco populado com sucesso.")
