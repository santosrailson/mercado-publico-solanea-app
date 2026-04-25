from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import Cessionario, Pagamento, Situacao
from app.schemas.schemas import DashboardData, DashboardKPIs, ChartData

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
def get_kpis(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Retorna indicadores chave (KPIs)"""
    total = db.query(Cessionario).count()
    regulares = db.query(Cessionario).filter(Cessionario.situacao == Situacao.REGULAR).count()
    irregulares = db.query(Cessionario).filter(Cessionario.situacao == Situacao.IRREGULAR).count()
    
    # Pagamentos do mês atual
    hoje = datetime.now()
    inicio_mes = datetime(hoje.year, hoje.month, 1)
    pagamentos_mes = db.query(func.sum(Pagamento.valor)).filter(
        Pagamento.data_pagamento >= inicio_mes
    ).scalar() or 0.0
    
    # Pagamentos da semana (últimos 7 dias)
    inicio_semana = hoje - timedelta(days=7)
    pagamentos_semana = db.query(func.sum(Pagamento.valor)).filter(
        Pagamento.data_pagamento >= inicio_semana
    ).scalar() or 0.0
    
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
    from app.crud.pagamento import get_pagamentos_por_mes
    
    dados = get_pagamentos_por_mes(db, meses=12)
    
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
    regulares = db.query(Cessionario).filter(Cessionario.situacao == Situacao.REGULAR).count()
    irregulares = db.query(Cessionario).filter(Cessionario.situacao == Situacao.IRREGULAR).count()
    
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
    result = db.query(
        Cessionario.nome,
        Cessionario.numero_box,
        func.sum(Pagamento.valor).label("total")
    ).join(Pagamento).group_by(Cessionario.id).order_by(
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
    pagamentos = db.query(Pagamento).join(Cessionario).order_by(
        Pagamento.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "tipo": "pagamento",
            "cessionario": p.cessionario.nome if p.cessionario else None,
            "valor": p.valor,
            "data": p.created_at
        }
        for p in pagamentos
    ]
