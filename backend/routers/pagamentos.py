import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from models import PagamentoCreate, PagamentoUpdate, PagamentoOut
from auth import get_current_user, require_admin

router = APIRouter(prefix="/pagamentos", tags=["pagamentos"])


async def row_to_pag(db, row) -> PagamentoOut:
    cess_nome = None
    cess_box = None
    async with db.execute(
        "SELECT nome, numero_box FROM cessionarios WHERE id = ?", (row["cessionario_id"],)
    ) as c:
        cr = await c.fetchone()
        if cr:
            cess_nome = cr["nome"]
            cess_box = cr["numero_box"]

    usuario_nome = None
    if row["usuario_id"]:
        async with db.execute("SELECT nome FROM users WHERE id = ?", (row["usuario_id"],)) as c:
            ur = await c.fetchone()
            if ur:
                usuario_nome = ur["nome"]

    return PagamentoOut(
        id=row["id"],
        cessionario_id=row["cessionario_id"],
        data=row["data"],
        valor=row["valor"],
        periodicidade=row["periodicidade"],
        observacao=row["observacao"],
        usuario_id=row["usuario_id"],
        criado_em=row["criado_em"],
        cessionario_nome=cess_nome,
        cessionario_box=cess_box,
        usuario_nome=usuario_nome,
    )


@router.get("", response_model=List[PagamentoOut])
async def list_pagamentos(user: dict = Depends(get_current_user)):
    async with get_db() as db:
        if user.get("is_admin"):
            async with db.execute("SELECT * FROM pagamentos ORDER BY data DESC") as c:
                rows = await c.fetchall()
        else:
            # User sees pagamentos of their cessionários
            async with db.execute(
                """SELECT p.* FROM pagamentos p
                   JOIN cessionarios c ON p.cessionario_id = c.id
                   WHERE c.criado_por = ?
                   ORDER BY p.data DESC""",
                (user["sub"],)
            ) as c:
                rows = await c.fetchall()
        return [await row_to_pag(db, r) for r in rows]


@router.post("", response_model=PagamentoOut, status_code=201)
async def create_pagamento(body: PagamentoCreate, user: dict = Depends(get_current_user)):
    async with get_db() as db:
        # Verify cessionario exists
        async with db.execute("SELECT * FROM cessionarios WHERE id = ?", (body.cessionario_id,)) as c:
            cess = await c.fetchone()
        if not cess:
            raise HTTPException(status_code=404, detail="Cessionário não encontrado")

        # Non-admin can only create pagamentos for their cessionários
        if not user.get("is_admin") and cess["criado_por"] != user["sub"]:
            raise HTTPException(status_code=403, detail="Sem permissão para este cessionário")

        pid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        await db.execute(
            """INSERT INTO pagamentos (id, cessionario_id, data, valor, periodicidade, observacao, usuario_id, criado_em)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (pid, body.cessionario_id, body.data, body.valor, body.periodicidade,
             body.observacao, user["sub"], now),
        )
        await db.commit()
        async with db.execute("SELECT * FROM pagamentos WHERE id = ?", (pid,)) as c:
            row = await c.fetchone()
        return await row_to_pag(db, row)


@router.patch("/{pid}", response_model=PagamentoOut)
async def update_pagamento(pid: str, body: PagamentoUpdate, _: dict = Depends(require_admin)):
    async with get_db() as db:
        async with db.execute("SELECT * FROM pagamentos WHERE id = ?", (pid,)) as c:
            row = await c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pagamento não encontrado")

        updates = {k: v for k, v in body.model_dump().items() if v is not None}
        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [pid]
            await db.execute(f"UPDATE pagamentos SET {set_clause} WHERE id = ?", values)
            await db.commit()

        async with db.execute("SELECT * FROM pagamentos WHERE id = ?", (pid,)) as c:
            row = await c.fetchone()
        return await row_to_pag(db, row)


@router.delete("/{pid}", status_code=204)
async def delete_pagamento(pid: str, _: dict = Depends(require_admin)):
    async with get_db() as db:
        async with db.execute("SELECT id FROM pagamentos WHERE id = ?", (pid,)) as c:
            if not await c.fetchone():
                raise HTTPException(status_code=404, detail="Pagamento não encontrado")
        await db.execute("DELETE FROM pagamentos WHERE id = ?", (pid,))
        await db.commit()
