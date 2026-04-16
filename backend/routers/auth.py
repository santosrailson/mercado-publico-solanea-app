from fastapi import APIRouter, HTTPException, Request, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from models import LoginRequest, TokenResponse, UserOut
from auth import verify_password, create_token, get_current_user

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    async with get_db() as db:
        async with db.execute(
            "SELECT * FROM users WHERE email = ?", (body.email,)
        ) as cursor:
            row = await cursor.fetchone()

    if not row or not verify_password(body.senha, row["senha_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = create_token({
        "sub": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "is_admin": bool(row["is_admin"]),
        "aprovado": bool(row["aprovado"]),
    })

    return TokenResponse(
        access_token=token,
        user_id=row["id"],
        nome=row["nome"],
        is_admin=bool(row["is_admin"]),
        aprovado=bool(row["aprovado"]),
    )


@router.get("/me", response_model=UserOut)
async def me(user: dict = Depends(get_current_user)):
    async with get_db() as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (user["sub"],)) as cursor:
            row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return UserOut(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        is_admin=bool(row["is_admin"]),
        aprovado=bool(row["aprovado"]),
        criado_por=row["criado_por"],
        criado_em=row["criado_em"],
    )
