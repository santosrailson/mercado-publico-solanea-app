from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import UserRole
from app.schemas.schemas import (
    CessionarioCreate, CessionarioUpdate, CessionarioResponse,
    CessionarioListFilters
)
from app.crud import cessionario as crud

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
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }


@router.get("", response_model=dict)
def list_cessionarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    situacao: Optional[str] = None,
    atividade: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Lista cessionários com paginação e filtros"""
    from app.models.models import Situacao
    
    sit_filter = None
    if situacao:
        try:
            sit_filter = Situacao(situacao)
        except ValueError:
            pass
    
    cessionarios, total = crud.get_cessionarios(
        db, skip=skip, limit=limit,
        search=search, situacao=sit_filter, atividade=atividade
    )
    
    # Converter para dict
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
    return crud.get_atividades_distintas(db)


@router.get("/{cessionario_id}", response_model=CessionarioResponse)
def get_cessionario(
    cessionario_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna detalhes de um cessionário"""
    cessionario = crud.get_cessionario(db, cessionario_id)
    if not cessionario:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    return cessionario


@router.post("", response_model=CessionarioResponse, status_code=201)
def create_cessionario(
    data: CessionarioCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Cria novo cessionário"""
    return crud.create_cessionario(db, data)


@router.put("/{cessionario_id}", response_model=CessionarioResponse)
def update_cessionario(
    cessionario_id: int,
    data: CessionarioUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Atualiza cessionário"""
    cessionario = crud.update_cessionario(db, cessionario_id, data)
    if not cessionario:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    return cessionario


@router.delete("/{cessionario_id}")
def delete_cessionario(
    cessionario_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Remove cessionário"""
    success = crud.delete_cessionario(db, cessionario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    return {"message": "Cessionário removido com sucesso"}
