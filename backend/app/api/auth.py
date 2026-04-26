from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import authenticate_user, create_access_token, get_current_user_id
from app.schemas.schemas import UserLogin, Token, UserResponse
from app.crud import user as crud_user

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


def user_to_dict(user) -> dict:
    """Converte usuário para dict com fiscal_id"""
    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": user.role.value if user.role else None,
        "status": user.status.value if user.status else None,
        "fiscal_id": user.fiscal_id,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.get("/me", response_model=dict)
def get_current_user_info(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user_to_dict(user)
