from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.security import get_current_user_id, verify_password
from app.models.models import UserRole, User
from app.schemas.schemas import UserCreate, UserUpdate, UserResponse, PasswordChange
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


@router.post("/change-password", response_model=dict)
def change_own_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Permite ao usuário alterar sua própria senha"""
    user = crud.get_user(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    crud.change_password(db, current_user_id, data.new_password)
    return {"message": "Senha alterada com sucesso"}


@router.put("/me", response_model=UserResponse)
def update_own_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Permite ao usuário atualizar seu próprio perfil (nome, email)"""
    # Não permite alterar role, status ou fiscal_id pelo próprio usuário
    update_dict = data.model_dump(exclude_unset=True)
    update_dict.pop("role", None)
    update_dict.pop("status", None)
    update_dict.pop("fiscal_id", None)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização")
    
    user = crud.update_user(db, current_user_id, UserUpdate(**update_dict))
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user
