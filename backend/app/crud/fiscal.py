from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime

from app.models.models import Fiscal
from app.schemas.schemas import FiscalCreate, FiscalUpdate


def get_fiscal(db: Session, fiscal_id: int) -> Optional[Fiscal]:
    return db.query(Fiscal).filter(Fiscal.id == fiscal_id).first()


def get_fiscais(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    ativo: Optional[bool] = None
) -> tuple[List[Fiscal], int]:
    query = db.query(Fiscal)
    
    if search:
        search_filter = or_(
            Fiscal.nome.ilike(f"%{search}%"),
            Fiscal.matricula.ilike(f"%{search}%"),
            Fiscal.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if ativo is not None:
        query = query.filter(Fiscal.ativo == ativo)
    
    total = query.count()
    fiscais = query.order_by(Fiscal.nome).offset(skip).limit(limit).all()
    
    return fiscais, total


def get_fiscais_ativos(db: Session) -> List[Fiscal]:
    return db.query(Fiscal).filter(Fiscal.ativo == True).order_by(Fiscal.nome).all()


def create_fiscal(db: Session, fiscal: FiscalCreate) -> Fiscal:
    db_fiscal = Fiscal(**fiscal.model_dump())
    db.add(db_fiscal)
    db.commit()
    db.refresh(db_fiscal)
    return db_fiscal


def update_fiscal(
    db: Session,
    fiscal_id: int,
    fiscal_update: FiscalUpdate
) -> Optional[Fiscal]:
    db_fiscal = get_fiscal(db, fiscal_id)
    if not db_fiscal:
        return None
    
    update_data = fiscal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_fiscal, field, value)
    
    db_fiscal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_fiscal)
    return db_fiscal


def delete_fiscal(db: Session, fiscal_id: int) -> bool:
    db_fiscal = get_fiscal(db, fiscal_id)
    if not db_fiscal:
        return False
    db.delete(db_fiscal)
    db.commit()
    return True
