from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.models import Pagamento, Cessionario, Periodicidade
from app.schemas.schemas import PagamentoCreate, PagamentoUpdate


def get_pagamento(db: Session, pagamento_id: int) -> Optional[Pagamento]:
    return db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()


def get_pagamentos(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    periodicidade: Optional[Periodicidade] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    cessionario_ids: Optional[List[int]] = None
) -> tuple[List[Pagamento], int]:
    query = db.query(Pagamento).join(Cessionario)
    
    if search:
        query = query.filter(Cessionario.nome.ilike(f"%{search}%"))
    
    if periodicidade:
        query = query.filter(Pagamento.periodicidade == periodicidade)
    
    if data_inicio:
        query = query.filter(Pagamento.data_pagamento >= data_inicio)
    
    if data_fim:
        query = query.filter(Pagamento.data_pagamento <= data_fim)
    
    if cessionario_ids:
        query = query.filter(Pagamento.cessionario_id.in_(cessionario_ids))
    
    total = query.count()
    pagamentos = query.order_by(desc(Pagamento.data_pagamento)).offset(skip).limit(limit).all()
    
    return pagamentos, total


def get_pagamentos_by_cessionario(
    db: Session,
    cessionario_id: int
) -> List[Pagamento]:
    return db.query(Pagamento).filter(
        Pagamento.cessionario_id == cessionario_id
    ).order_by(desc(Pagamento.data_pagamento)).all()


def create_pagamento(
    db: Session,
    pagamento: PagamentoCreate,
    registrado_por_id: Optional[int] = None
) -> Pagamento:
    db_pagamento = Pagamento(
        **pagamento.model_dump(),
        registrado_por_id=registrado_por_id
    )
    db.add(db_pagamento)
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento


def update_pagamento(
    db: Session,
    pagamento_id: int,
    pagamento_update: PagamentoUpdate
) -> Optional[Pagamento]:
    db_pagamento = get_pagamento(db, pagamento_id)
    if not db_pagamento:
        return None
    
    update_data = pagamento_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_pagamento, field, value)
    
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento


def delete_pagamento(db: Session, pagamento_id: int) -> bool:
    db_pagamento = get_pagamento(db, pagamento_id)
    if not db_pagamento:
        return False
    db.delete(db_pagamento)
    db.commit()
    return True


def get_arrecadacao_periodo(
    db: Session,
    data_inicio: datetime,
    data_fim: datetime
) -> float:
    result = db.query(func.sum(Pagamento.valor)).filter(
        Pagamento.data_pagamento >= data_inicio,
        Pagamento.data_pagamento <= data_fim
    ).scalar()
    return result or 0.0


def get_pagamentos_por_mes(db: Session, meses: int = 12) -> dict:
    """Retorna arrecadação dos últimos N meses para gráficos"""
    hoje = datetime.now()
    dados = {}
    
    for i in range(meses - 1, -1, -1):
        data_base = hoje - timedelta(days=i * 30)
        mes_ano = data_base.strftime("%m/%Y")
        
        inicio_mes = datetime(data_base.year, data_base.month, 1)
        if data_base.month == 12:
            fim_mes = datetime(data_base.year + 1, 1, 1)
        else:
            fim_mes = datetime(data_base.year, data_base.month + 1, 1)
        
        total = db.query(func.sum(Pagamento.valor)).filter(
            Pagamento.data_pagamento >= inicio_mes,
            Pagamento.data_pagamento < fim_mes
        ).scalar() or 0.0
        
        dados[mes_ano] = total
    
    return dados
