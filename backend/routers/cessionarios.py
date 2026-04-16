import uuid
from datetime import datetime, date, timedelta
from typing import List
from collections import Counter

from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from models import (
    CessionarioCreate, CessionarioUpdate, CessionarioOut, CertidaoResponse
)
from auth import get_current_user, require_admin

router = APIRouter(prefix="/cessionarios", tags=["cessionarios"])


async def row_to_cess(db, row) -> CessionarioOut:
    # Get cadastrador name
    cadastrador_nome = None
    if row["criado_por"]:
        async with db.execute("SELECT nome FROM users WHERE id = ?", (row["criado_por"],)) as c:
            u = await c.fetchone()
            if u:
                cadastrador_nome = u["nome"]

    # Total pago e último pagamento
    async with db.execute(
        "SELECT SUM(valor) as total, MAX(data) as ultimo FROM pagamentos WHERE cessionario_id = ?",
        (row["id"],)
    ) as c:
        pr = await c.fetchone()
    total_pago = pr["total"] or 0.0
    ultimo_pagamento = pr["ultimo"]

    return CessionarioOut(
        id=row["id"],
        nome=row["nome"],
        numero_box=row["numero_box"],
        atividade=row["atividade"],
        telefone=row["telefone"],
        situacao=row["situacao"],
        valor_ref=row["valor_ref"],
        per_ref=row["per_ref"],
        observacao=row["observacao"],
        criado_por=row["criado_por"],
        criado_em=row["criado_em"],
        cadastrador_nome=cadastrador_nome,
        total_pago=total_pago,
        ultimo_pagamento=ultimo_pagamento,
    )


def detectar_ausencias(pagamentos: list, periodicidade: str) -> list:
    """Detecta períodos sem pagamento desde o primeiro pagamento até hoje."""
    ausencias = []
    if not pagamentos:
        return ausencias

    datas = sorted([p["data"] for p in pagamentos])
    primeira = date.fromisoformat(datas[0])
    hoje = date.today()

    if periodicidade == "Mensal":
        # Meses com pelo menos um pagamento
        meses_pagos = set()
        for d in datas:
            dt = date.fromisoformat(d)
            meses_pagos.add((dt.year, dt.month))

        # Itera apenas até o mês anterior ao atual (mês corrente ainda não fechou)
        mes_anterior = date(hoje.year, hoje.month, 1) - timedelta(days=1)
        limite = date(mes_anterior.year, mes_anterior.month, 1)

        cur = date(primeira.year, primeira.month, 1)
        while cur <= limite:
            if (cur.year, cur.month) not in meses_pagos:
                nomes = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
                ausencias.append(f"{nomes[cur.month - 1]} de {cur.year}")
            if cur.month == 12:
                cur = date(cur.year + 1, 1, 1)
            else:
                cur = date(cur.year, cur.month + 1, 1)

    elif periodicidade == "Semanal":
        # Weeks (Monday) with at least one payment — só semanas já encerradas
        semanas_pagas = set()
        for d in datas:
            dt = date.fromisoformat(d)
            segunda = dt - timedelta(days=dt.weekday())
            semanas_pagas.add(segunda)

        semana_atual = hoje - timedelta(days=hoje.weekday())
        cur = primeira - timedelta(days=primeira.weekday())
        while cur < semana_atual:
            if cur not in semanas_pagas:
                fim = cur + timedelta(days=6)
                ausencias.append(f"Semana de {cur.strftime('%d/%m')} a {fim.strftime('%d/%m/%Y')}")
            cur += timedelta(weeks=1)

    elif periodicidade == "Quinzenal":
        # Two-week periods — só períodos já encerrados
        periodos_pagos = set()
        ref = date(primeira.year, primeira.month, 1)
        for d in datas:
            dt = date.fromisoformat(d)
            days_since = (dt - ref).days
            periodo = days_since // 15
            periodos_pagos.add(periodo)

        cur = ref
        periodo_idx = 0
        while cur + timedelta(days=14) < hoje:
            if periodo_idx not in periodos_pagos:
                fim = cur + timedelta(days=14)
                ausencias.append(f"Quinzena de {cur.strftime('%d/%m')} a {fim.strftime('%d/%m/%Y')}")
            cur += timedelta(days=15)
            periodo_idx += 1

    return ausencias


@router.get("", response_model=List[CessionarioOut])
async def list_cessionarios(user: dict = Depends(get_current_user)):
    async with get_db() as db:
        if user.get("is_admin"):
            async with db.execute("SELECT * FROM cessionarios ORDER BY nome") as c:
                rows = await c.fetchall()
        else:
            async with db.execute(
                "SELECT * FROM cessionarios WHERE criado_por = ? ORDER BY nome", (user["sub"],)
            ) as c:
                rows = await c.fetchall()
        return [await row_to_cess(db, r) for r in rows]


@router.post("", response_model=CessionarioOut, status_code=201)
async def create_cessionario(body: CessionarioCreate, user: dict = Depends(get_current_user)):
    cid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    async with get_db() as db:
        await db.execute(
            """INSERT INTO cessionarios
               (id, nome, numero_box, atividade, telefone, situacao, valor_ref, per_ref, observacao, criado_por, criado_em)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (cid, body.nome, body.numero_box, body.atividade, body.telefone,
             body.situacao, body.valor_ref, body.per_ref, body.observacao,
             user["sub"], now),
        )
        await db.commit()
        async with db.execute("SELECT * FROM cessionarios WHERE id = ?", (cid,)) as c:
            row = await c.fetchone()
        return await row_to_cess(db, row)


@router.patch("/{cid}", response_model=CessionarioOut)
async def update_cessionario(cid: str, body: CessionarioUpdate, user: dict = Depends(get_current_user)):
    async with get_db() as db:
        async with db.execute("SELECT * FROM cessionarios WHERE id = ?", (cid,)) as c:
            row = await c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Cessionário não encontrado")
        if not user.get("is_admin") and row["criado_por"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Sem permissão")

        updates = {k: v for k, v in body.model_dump().items() if v is not None}
        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [cid]
            await db.execute(f"UPDATE cessionarios SET {set_clause} WHERE id = ?", values)
            await db.commit()

        async with db.execute("SELECT * FROM cessionarios WHERE id = ?", (cid,)) as c:
            row = await c.fetchone()
        return await row_to_cess(db, row)


@router.delete("/{cid}", status_code=204)
async def delete_cessionario(cid: str, user: dict = Depends(get_current_user)):
    async with get_db() as db:
        async with db.execute("SELECT * FROM cessionarios WHERE id = ?", (cid,)) as c:
            row = await c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Cessionário não encontrado")
        if not user.get("is_admin") and row["criado_por"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Sem permissão")
        # Cascade delete pagamentos
        await db.execute("DELETE FROM pagamentos WHERE cessionario_id = ?", (cid,))
        await db.execute("DELETE FROM cessionarios WHERE id = ?", (cid,))
        await db.commit()


@router.get("/{cid}/certidao", response_model=CertidaoResponse)
async def certidao(cid: str, user: dict = Depends(get_current_user)):
    async with get_db() as db:
        async with db.execute("SELECT * FROM cessionarios WHERE id = ?", (cid,)) as c:
            cess = await c.fetchone()
        if not cess:
            raise HTTPException(status_code=404, detail="Cessionário não encontrado")
        if not user.get("is_admin") and cess["criado_por"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Sem permissão")

        async with db.execute(
            "SELECT * FROM pagamentos WHERE cessionario_id = ? ORDER BY data", (cid,)
        ) as c:
            pags = await c.fetchall()

        async with db.execute("SELECT nome FROM users WHERE id = ?", (user["sub"],)) as c:
            u = await c.fetchone()
        emitido_por = u["nome"] if u else user.get("nome", "Sistema")

    pagamentos_list = [dict(p) for p in pags]

    # Determine periodicidade predominante
    if pagamentos_list:
        counter = Counter(p["periodicidade"] for p in pagamentos_list)
        periodicidade = counter.most_common(1)[0][0]
    else:
        periodicidade = cess["per_ref"] or "Mensal"

    ausencias = detectar_ausencias(pagamentos_list, periodicidade)
    ultimo = max((p["data"] for p in pagamentos_list), default=None)
    total_pago = sum(p["valor"] for p in pagamentos_list)

    # Situação é derivada das ausências calculadas, não do campo manual
    situacao_calculada = "Irregular" if ausencias else "Regular"

    # Sincroniza o campo no banco para refletir a realidade
    async with get_db() as db2:
        await db2.execute(
            "UPDATE cessionarios SET situacao = ? WHERE id = ?",
            (situacao_calculada, cid),
        )
        await db2.commit()

    numero = f"CERT-{cid[:8].upper()}-{datetime.utcnow().strftime('%Y%m%d')}"

    return CertidaoResponse(
        numero=numero,
        cessionario=cess["nome"],
        numero_box=cess["numero_box"],
        atividade=cess["atividade"],
        situacao=situacao_calculada,
        ausencias=ausencias,
        ultimo_pagamento=ultimo,
        periodicidade=periodicidade,
        emitido_em=datetime.utcnow().isoformat(),
        emitido_por=emitido_por,
        total_pago=total_pago,
        valor_ref=cess["valor_ref"],
    )
