import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Depends

from database import get_db
from models import UserCreate, UserUpdate, UserOut
from auth import get_current_user, require_admin, hash_password

router = APIRouter(prefix="/users", tags=["users"])


def row_to_user(row) -> UserOut:
    return UserOut(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        is_admin=bool(row["is_admin"]),
        aprovado=bool(row["aprovado"]),
        criado_por=row["criado_por"],
        criado_em=row["criado_em"],
    )


@router.get("", response_model=List[UserOut])
async def list_users(_: dict = Depends(require_admin)):
    async with get_db() as db:
        async with db.execute("SELECT * FROM users ORDER BY criado_em DESC") as cursor:
            rows = await cursor.fetchall()
    return [row_to_user(r) for r in rows]


@router.post("", response_model=UserOut, status_code=201)
async def create_user(body: UserCreate, admin: dict = Depends(require_admin)):
    uid = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    async with get_db() as db:
        # Check duplicate email
        async with db.execute("SELECT id FROM users WHERE email = ?", (body.email,)) as c:
            if await c.fetchone():
                raise HTTPException(status_code=409, detail="Email já cadastrado")
        await db.execute(
            """INSERT INTO users (id, nome, email, senha_hash, is_admin, aprovado, criado_por, criado_em)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (uid, body.nome, body.email, hash_password(body.senha),
             int(body.is_admin), 1, admin["sub"], now),
        )
        await db.commit()
        async with db.execute("SELECT * FROM users WHERE id = ?", (uid,)) as c:
            row = await c.fetchone()
    return row_to_user(row)


@router.patch("/{uid}", response_model=UserOut)
async def update_user(uid: str, body: UserUpdate, user: dict = Depends(get_current_user)):
    # Admin or own user
    if not user.get("is_admin") and user["sub"] != uid:
        raise HTTPException(status_code=403, detail="Sem permissão")

    async with get_db() as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (uid,)) as c:
            row = await c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        updates = {}
        if body.nome is not None:
            updates["nome"] = body.nome
        if body.email is not None:
            updates["email"] = body.email
        if body.senha is not None:
            updates["senha_hash"] = hash_password(body.senha)
        if body.is_admin is not None and user.get("is_admin"):
            updates["is_admin"] = int(body.is_admin)
        if body.aprovado is not None and user.get("is_admin"):
            updates["aprovado"] = int(body.aprovado)

        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [uid]
            await db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
            await db.commit()

        async with db.execute("SELECT * FROM users WHERE id = ?", (uid,)) as c:
            row = await c.fetchone()
    return row_to_user(row)


@router.delete("/{uid}", status_code=204)
async def delete_user(uid: str, admin: dict = Depends(require_admin)):
    if uid == admin["sub"]:
        raise HTTPException(status_code=400, detail="Não é possível deletar a si mesmo")
    async with get_db() as db:
        async with db.execute("SELECT id FROM users WHERE id = ?", (uid,)) as c:
            if not await c.fetchone():
                raise HTTPException(status_code=404, detail="Usuário não encontrado")
        await db.execute("DELETE FROM users WHERE id = ?", (uid,))
        await db.commit()


@router.post("/{uid}/aprovar", response_model=UserOut)
async def aprovar_user(uid: str, _: dict = Depends(require_admin)):
    async with get_db() as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (uid,)) as c:
            row = await c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        await db.execute("UPDATE users SET aprovado = 1 WHERE id = ?", (uid,))
        await db.commit()
        async with db.execute("SELECT * FROM users WHERE id = ?", (uid,)) as c:
            row = await c.fetchone()
    return row_to_user(row)
