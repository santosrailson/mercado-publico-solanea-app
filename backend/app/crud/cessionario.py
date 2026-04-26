from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, desc
from typing import List, Optional
from datetime import datetime

from app.models.models import Cessionario, Situacao, Pagamento
from app.schemas.schemas import CessionarioCreate, CessionarioUpdate


def get_cessionario(db: Session, cessionario_id: int) -> Optional[Cessionario]:
    return db.query(Cessionario).options(joinedload(Cessionario.fiscal)).filter(Cessionario.id == cessionario_id).first()


def get_cessionarios(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    situacao: Optional[Situacao] = None,
    atividade: Optional[str] = None,
    fiscal_id: Optional[int] = None
) -> tuple[List[Cessionario], int]:
    query = db.query(Cessionario)
    
    if search:
        search_filter = or_(
            Cessionario.nome.ilike(f"%{search}%"),
            Cessionario.numero_box.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if situacao:
        query = query.filter(Cessionario.situacao == situacao)
    
    if atividade:
        query = query.filter(Cessionario.atividade.ilike(f"%{atividade}%"))
    
    if fiscal_id is not None:
        query = query.filter(Cessionario.fiscal_id == fiscal_id)
    
    total = query.count()
    cessionarios = query.options(joinedload(Cessionario.fiscal)).order_by(Cessionario.nome).offset(skip).limit(limit).all()
    
    return cessionarios, total


def get_cessionarios_by_situacao(
    db: Session,
    situacao: Situacao
) -> List[Cessionario]:
    return db.query(Cessionario).filter(
        Cessionario.situacao == situacao
    ).order_by(Cessionario.nome).all()


def create_cessionario(db: Session, cessionario: CessionarioCreate) -> Cessionario:
    db_cessionario = Cessionario(**cessionario.model_dump())
    db.add(db_cessionario)
    db.commit()
    db.refresh(db_cessionario)
    return db_cessionario


def update_cessionario(
    db: Session,
    cessionario_id: int,
    cessionario_update: CessionarioUpdate
) -> Optional[Cessionario]:
    db_cessionario = get_cessionario(db, cessionario_id)
    if not db_cessionario:
        return None
    
    update_data = cessionario_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cessionario, field, value)
    
    db_cessionario.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_cessionario)
    return db_cessionario


def delete_cessionario(db: Session, cessionario_id: int) -> bool:
    db_cessionario = get_cessionario(db, cessionario_id)
    if not db_cessionario:
        return False
    db.delete(db_cessionario)
    db.commit()
    return True


def get_atividades_distintas(db: Session, fiscal_id: Optional[int] = None) -> List[str]:
    query = db.query(Cessionario.atividade).distinct().filter(
        Cessionario.atividade != None
    )
    if fiscal_id is not None:
        query = query.filter(Cessionario.fiscal_id == fiscal_id)
    result = query.all()
    return [r[0] for r in result if r[0]]


def get_ultimo_pagamento(db: Session, cessionario_id: int) -> Optional[datetime]:
    result = db.query(Pagamento).filter(
        Pagamento.cessionario_id == cessionario_id
    ).order_by(desc(Pagamento.data_pagamento)).first()
    
    return result.data_pagamento if result else None
