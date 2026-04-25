from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import UserRole
from app.schemas.schemas import UserCreate, UserUpdate, UserResponse
from app.crud import user as crud

router = APIRouter(prefix="/users", tags=["Usuários"])


def check_admin(user_id: int, db: Session):
    """Verifica se usuário é admin"""
    user = crud.get_user(db, user_id)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")


@router.get("", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Lista todos os usuários (apenas admin)"""
    check_admin(current_user_id, db)
    return crud.get_users(db)


@router.get("/pending-count")
def get_pending_count(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna quantidade de usuários pendentes"""
    check_admin(current_user_id, db)
    return {"count": crud.get_pending_users_count(db)}


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Cria novo usuário"""
    check_admin(current_user_id, db)
    
    # Verifica se email já existe
    existing = crud.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    return crud.create_user(db, data)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Atualiza usuário"""
    check_admin(current_user_id, db)
    
    user = crud.update_user(db, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.post("/{user_id}/approve")
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Aprova usuário pendente"""
    check_admin(current_user_id, db)
    
    user = crud.approve_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário aprovado com sucesso"}


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Remove usuário"""
    check_admin(current_user_id, db)
    
    # Não permite remover a si mesmo
    if user_id == current_user_id:
        raise HTTPException(status_code=400, detail="Não pode remover seu próprio usuário")
    
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário removido com sucesso"}
