from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import UserRole
from app.schemas.schemas import FiscalCreate, FiscalUpdate, FiscalResponse
from app.crud import fiscal as crud
from app.crud import user as user_crud

router = APIRouter(prefix="/fiscais", tags=["Fiscais"])


def fiscal_to_dict(f) -> dict:
    """Converte modelo Fiscal para dict serializável"""
    return {
        "id": f.id,
        "nome": f.nome,
        "matricula": f.matricula,
        "telefone": f.telefone,
        "email": f.email,
        "ativo": f.ativo,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    }


def check_admin(user_id: int, db: Session):
    """Verifica se usuário é admin"""
    user = user_crud.get_user(db, user_id)
    if not user or user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")


@router.get("", response_model=dict)
def list_fiscais(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Lista fiscais com paginação e filtros (apenas admin)"""
    check_admin(current_user_id, db)
    
    fiscais, total = crud.get_fiscais(db, skip=skip, limit=limit, search=search, ativo=ativo)
    
    return {
        "items": [fiscal_to_dict(f) for f in fiscais],
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }


@router.get("/ativos", response_model=List[FiscalResponse])
def list_fiscais_ativos(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna lista de fiscais ativos (qualquer usuário autenticado)"""
    return crud.get_fiscais_ativos(db)


@router.get("/{fiscal_id}", response_model=FiscalResponse)
def get_fiscal(
    fiscal_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna detalhes de um fiscal (apenas admin)"""
    check_admin(current_user_id, db)
    
    fiscal = crud.get_fiscal(db, fiscal_id)
    if not fiscal:
        raise HTTPException(status_code=404, detail="Fiscal não encontrado")
    return fiscal


@router.post("", response_model=FiscalResponse, status_code=201)
def create_fiscal(
    data: FiscalCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Cria novo fiscal (apenas admin)"""
    check_admin(current_user_id, db)
    return crud.create_fiscal(db, data)


@router.put("/{fiscal_id}", response_model=FiscalResponse)
def update_fiscal(
    fiscal_id: int,
    data: FiscalUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Atualiza fiscal (apenas admin)"""
    check_admin(current_user_id, db)
    
    fiscal = crud.update_fiscal(db, fiscal_id, data)
    if not fiscal:
        raise HTTPException(status_code=404, detail="Fiscal não encontrado")
    return fiscal


@router.delete("/{fiscal_id}")
def delete_fiscal(
    fiscal_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Remove fiscal (apenas admin)"""
    check_admin(current_user_id, db)
    
    success = crud.delete_fiscal(db, fiscal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Fiscal não encontrado")
    return {"message": "Fiscal removido com sucesso"}
