from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.schemas.schemas import (
    PagamentoCreate, PagamentoUpdate, PagamentoResponse
)
from app.crud import pagamento as crud
from app.crud import cessionario as crud_cess
from app.crud import user as crud_user
from app.models.models import Periodicidade, UserRole

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])


def pagamento_to_dict(p) -> dict:
    """Converte modelo SQLAlchemy para dict"""
    return {
        "id": p.id,
        "cessionario_id": p.cessionario_id,
        "cessionario_nome": p.cessionario.nome if p.cessionario else None,
        "cessionario_telefone": p.cessionario.telefone if p.cessionario else None,
        "valor": p.valor,
        "data_pagamento": p.data_pagamento.isoformat() if p.data_pagamento else None,
        "periodicidade": p.periodicidade.value if p.periodicidade else None,
        "referencia_mes": p.referencia_mes,
        "observacoes": p.observacoes,
        "registrado_por_nome": p.registrado_por.nome if p.registrado_por else None,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def get_current_user(db: Session, user_id: int):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.get("", response_model=dict)
def list_pagamentos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    periodicidade: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Lista pagamentos com paginação e filtros"""
    user = get_current_user(db, current_user_id)
    
    per_filter = None
    if periodicidade:
        try:
            per_filter = Periodicidade(periodicidade)
        except ValueError:
            pass
    
    # Se for fiscal (não admin), filtra apenas pagamentos de seus cessionários
    cessionario_ids = None
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        cessionarios, _ = crud_cess.get_cessionarios(
            db, skip=0, limit=10000, fiscal_id=user.fiscal_id
        )
        cessionario_ids = [c.id for c in cessionarios]
    
    pagamentos, total = crud.get_pagamentos(
        db, skip=skip, limit=limit,
        search=search, periodicidade=per_filter,
        data_inicio=data_inicio, data_fim=data_fim,
        cessionario_ids=cessionario_ids
    )
    
    # Converter para dict
    items = [pagamento_to_dict(p) for p in pagamentos]
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "pages": (total + limit - 1) // limit if limit > 0 else 1
    }


@router.get("/cessionario/{cessionario_id}", response_model=List[dict])
def get_pagamentos_by_cessionario(
    cessionario_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna todos os pagamentos de um cessionário"""
    user = get_current_user(db, current_user_id)
    
    # Verifica se fiscal pode acessar este cessionário
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        cessionario = crud_cess.get_cessionario(db, cessionario_id)
        if not cessionario or cessionario.fiscal_id != user.fiscal_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para acessar os pagamentos deste cessionário")
    
    pagamentos = crud.get_pagamentos_by_cessionario(db, cessionario_id)
    return [pagamento_to_dict(p) for p in pagamentos]


@router.post("", response_model=dict, status_code=201)
def create_pagamento(
    data: PagamentoCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Registra novo pagamento"""
    user = get_current_user(db, current_user_id)
    
    # Verifica se fiscal pode registrar pagamento para este cessionário
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        cessionario = crud_cess.get_cessionario(db, data.cessionario_id)
        if not cessionario or cessionario.fiscal_id != user.fiscal_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para registrar pagamentos deste cessionário")
    
    pagamento = crud.create_pagamento(db, data, registrado_por_id=current_user_id)
    return pagamento_to_dict(pagamento)


@router.put("/{pagamento_id}", response_model=dict)
def update_pagamento(
    pagamento_id: int,
    data: PagamentoUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Atualiza pagamento"""
    user = get_current_user(db, current_user_id)
    
    # Verifica se fiscal pode atualizar este pagamento
    existing = crud.get_pagamento(db, pagamento_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        cessionario = crud_cess.get_cessionario(db, existing.cessionario_id)
        if not cessionario or cessionario.fiscal_id != user.fiscal_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para atualizar este pagamento")
    
    pagamento = crud.update_pagamento(db, pagamento_id, data)
    return pagamento_to_dict(pagamento)


@router.delete("/{pagamento_id}")
def delete_pagamento(
    pagamento_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Remove pagamento"""
    user = get_current_user(db, current_user_id)
    
    # Verifica se fiscal pode remover este pagamento
    existing = crud.get_pagamento(db, pagamento_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        cessionario = crud_cess.get_cessionario(db, existing.cessionario_id)
        if not cessionario or cessionario.fiscal_id != user.fiscal_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para remover este pagamento")
    
    success = crud.delete_pagamento(db, pagamento_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return {"message": "Pagamento removido com sucesso"}
