from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import UserRole, User
from app.schemas.schemas import (
    CessionarioCreate, CessionarioUpdate, CessionarioResponse,
    CessionarioListFilters
)
from app.crud import cessionario as crud
from app.crud import user as crud_user

router = APIRouter(prefix="/cessionarios", tags=["Cessionários"])


def cessionario_to_dict(c) -> dict:
    """Converte modelo SQLAlchemy para dict"""
    return {
        "id": c.id,
        "nome": c.nome,
        "numero_box": c.numero_box,
        "atividade": c.atividade,
        "telefone": c.telefone,
        "situacao": c.situacao.value if c.situacao else None,
        "valor_referencia": c.valor_referencia,
        "periodicidade_referencia": c.periodicidade_referencia.value if c.periodicidade_referencia else None,
        "observacoes": c.observacoes,
        "fiscal_id": c.fiscal_id,
        "fiscal_nome": c.fiscal.nome if c.fiscal else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


def get_current_user(db: Session, user_id: int) -> User:
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def check_cessionario_ownership(cessionario, user: User):
    """Verifica se um fiscal pode acessar/modificar um cessionário"""
    if user.role == UserRole.ADMIN:
        return True
    if user.fiscal_id is not None and cessionario.fiscal_id == user.fiscal_id:
        return True
    raise HTTPException(status_code=403, detail="Você não tem permissão para acessar este cessionário")


@router.get("", response_model=dict)
def list_cessionarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    situacao: Optional[str] = None,
    atividade: Optional[str] = None,
    fiscal_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Lista cessionários com paginação e filtros"""
    from app.models.models import Situacao
    
    user = get_current_user(db, current_user_id)
    
    # Se for fiscal (não admin), filtra apenas seus cessionários
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        fiscal_id = user.fiscal_id
    
    sit_filter = None
    if situacao:
        try:
            sit_filter = Situacao(situacao)
        except ValueError:
            pass
    
    cessionarios, total = crud.get_cessionarios(
        db, skip=skip, limit=limit,
        search=search, situacao=sit_filter, atividade=atividade, fiscal_id=fiscal_id
    )
    
    # Converter para dict com informação do fiscal
    items = [cessionario_to_dict(c) for c in cessionarios]
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }


@router.get("/atividades", response_model=List[str])
def get_atividades(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna lista de atividades distintas para filtros"""
    user = get_current_user(db, current_user_id)
    
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        return crud.get_atividades_distintas(db, fiscal_id=user.fiscal_id)
    
    return crud.get_atividades_distintas(db)


@router.get("/{cessionario_id}", response_model=dict)
def get_cessionario(
    cessionario_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna detalhes de um cessionário"""
    user = get_current_user(db, current_user_id)
    
    cessionario = crud.get_cessionario(db, cessionario_id)
    if not cessionario:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    
    check_cessionario_ownership(cessionario, user)
    return cessionario_to_dict(cessionario)


@router.post("", response_model=dict, status_code=201)
def create_cessionario(
    data: CessionarioCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Cria novo cessionário"""
    user = get_current_user(db, current_user_id)
    
    # Se for fiscal (não admin), auto-preenche fiscal_id
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        data.fiscal_id = user.fiscal_id
    
    novo = crud.create_cessionario(db, data)
    # Recarrega com relacionamento fiscal
    return cessionario_to_dict(crud.get_cessionario(db, novo.id))


@router.put("/{cessionario_id}", response_model=dict)
def update_cessionario(
    cessionario_id: int,
    data: CessionarioUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Atualiza cessionário"""
    user = get_current_user(db, current_user_id)
    
    cessionario = crud.get_cessionario(db, cessionario_id)
    if not cessionario:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    
    check_cessionario_ownership(cessionario, user)
    
    # Fiscal não pode alterar o fiscal_id
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        data.fiscal_id = user.fiscal_id
    
    updated = crud.update_cessionario(db, cessionario_id, data)
    # Recarrega com relacionamento fiscal
    return cessionario_to_dict(crud.get_cessionario(db, updated.id))


@router.delete("/{cessionario_id}")
def delete_cessionario(
    cessionario_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Remove cessionário"""
    user = get_current_user(db, current_user_id)
    
    cessionario = crud.get_cessionario(db, cessionario_id)
    if not cessionario:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    
    check_cessionario_ownership(cessionario, user)
    
    success = crud.delete_cessionario(db, cessionario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    return {"message": "Cessionário removido com sucesso"}
