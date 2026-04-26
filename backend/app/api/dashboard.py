from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import Cessionario, Pagamento, Situacao, UserRole, User
from app.schemas.schemas import DashboardData, DashboardKPIs, ChartData
from app.crud import user as crud_user
from app.crud import cessionario as crud_cess

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_current_user(db: Session, user_id: int) -> User:
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def get_fiscal_filter(user: User) -> int | None:
    """Retorna fiscal_id se o usuário for um fiscal (não admin)"""
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        return user.fiscal_id
    return None


@router.get("/kpis", response_model=DashboardKPIs)
def get_kpis(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna indicadores chave (KPIs)"""
    user = get_current_user(db, current_user_id)
    fiscal_id = get_fiscal_filter(user)
    
    query = db.query(Cessionario)
    if fiscal_id is not None:
        query = query.filter(Cessionario.fiscal_id == fiscal_id)
    
    total = query.count()
    regulares = query.filter(Cessionario.situacao == Situacao.REGULAR).count()
    irregulares = query.filter(Cessionario.situacao == Situacao.IRREGULAR).count()
    
    # Pagamentos do mês atual
    hoje = datetime.now()
    inicio_mes = datetime(hoje.year, hoje.month, 1)
    
    pag_query = db.query(func.sum(Pagamento.valor)).filter(
        Pagamento.data_pagamento >= inicio_mes
    )
    if fiscal_id is not None:
        cessionarios, _ = crud_cess.get_cessionarios(db, skip=0, limit=10000, fiscal_id=fiscal_id)
        cessionario_ids = [c.id for c in cessionarios]
        pag_query = pag_query.filter(Pagamento.cessionario_id.in_(cessionario_ids))
    
    pagamentos_mes = pag_query.scalar() or 0.0
    
    # Pagamentos da semana (últimos 7 dias)
    inicio_semana = hoje - timedelta(days=7)
    pag_query_semana = db.query(func.sum(Pagamento.valor)).filter(
        Pagamento.data_pagamento >= inicio_semana
    )
    if fiscal_id is not None:
        pag_query_semana = pag_query_semana.filter(Pagamento.cessionario_id.in_(cessionario_ids))
    
    pagamentos_semana = pag_query_semana.scalar() or 0.0
    
    return DashboardKPIs(
        total_cessionarios=total,
        total_regulares=regulares,
        total_irregulares=irregulares,
        total_pagamentos_mes=pagamentos_mes,
        total_pagamentos_semana=pagamentos_semana
    )


@router.get("/charts/arrecadacao", response_model=ChartData)
def get_arrecadacao_chart(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna dados de arrecadação dos últimos 12 meses para gráfico"""
    user = get_current_user(db, current_user_id)
    fiscal_id = get_fiscal_filter(user)
    
    hoje = datetime.now()
    dados = {}
    
    # Obtém IDs dos cessionários do fiscal se aplicável
    cessionario_ids = None
    if fiscal_id is not None:
        cessionarios, _ = crud_cess.get_cessionarios(db, skip=0, limit=10000, fiscal_id=fiscal_id)
        cessionario_ids = [c.id for c in cessionarios]
    
    for i in range(11, -1, -1):
        data_base = hoje - timedelta(days=i * 30)
        mes_ano = data_base.strftime("%m/%Y")
        
        inicio_mes = datetime(data_base.year, data_base.month, 1)
        if data_base.month == 12:
            fim_mes = datetime(data_base.year + 1, 1, 1)
        else:
            fim_mes = datetime(data_base.year, data_base.month + 1, 1)
        
        query = db.query(func.sum(Pagamento.valor)).filter(
            Pagamento.data_pagamento >= inicio_mes,
            Pagamento.data_pagamento < fim_mes
        )
        
        if cessionario_ids:
            query = query.filter(Pagamento.cessionario_id.in_(cessionario_ids))
        
        total = query.scalar() or 0.0
        dados[mes_ano] = total
    
    return ChartData(
        labels=list(dados.keys()),
        values=list(dados.values())
    )


@router.get("/charts/situacao", response_model=ChartData)
def get_situacao_chart(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna dados de situação dos cessionários para gráfico de pizza/donut"""
    user = get_current_user(db, current_user_id)
    fiscal_id = get_fiscal_filter(user)
    
    query = db.query(Cessionario)
    if fiscal_id is not None:
        query = query.filter(Cessionario.fiscal_id == fiscal_id)
    
    regulares = query.filter(Cessionario.situacao == Situacao.REGULAR).count()
    irregulares = query.filter(Cessionario.situacao == Situacao.IRREGULAR).count()
    
    return ChartData(
        labels=["Regulares", "Irregulares"],
        values=[regulares, irregulares]
    )


@router.get("/top-cessionarios", response_model=list)
def get_top_cessionarios(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna top cessionários com mais pagamentos"""
    user = get_current_user(db, current_user_id)
    fiscal_id = get_fiscal_filter(user)
    
    query = db.query(
        Cessionario.nome,
        Cessionario.numero_box,
        func.sum(Pagamento.valor).label("total")
    ).join(Pagamento).group_by(Cessionario.id)
    
    if fiscal_id is not None:
        query = query.filter(Cessionario.fiscal_id == fiscal_id)
    
    result = query.order_by(
        func.sum(Pagamento.valor).desc()
    ).limit(limit).all()
    
    return [
        {"nome": r.nome, "box": r.numero_box, "total": r.total}
        for r in result
    ]


@router.get("/atividades-recentes", response_model=list)
def get_atividades_recentes(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna atividades recentes (últimos pagamentos)"""
    user = get_current_user(db, current_user_id)
    fiscal_id = get_fiscal_filter(user)
    
    query = db.query(Pagamento).join(Cessionario).order_by(
        Pagamento.created_at.desc()
    )
    
    if fiscal_id is not None:
        query = query.filter(Cessionario.fiscal_id == fiscal_id)
    
    pagamentos = query.limit(limit).all()
    
    return [
        {
            "tipo": "pagamento",
            "cessionario": p.cessionario.nome if p.cessionario else None,
            "valor": p.valor,
            "data": p.created_at
        }
        for p in pagamentos
    ]
