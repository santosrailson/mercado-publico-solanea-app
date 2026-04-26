from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import Situacao
from app.schemas.schemas import RelatorioFiltros
from app.crud import cessionario as crud_cess
from app.crud import pagamento as crud_pag
from app.services.pdf_service import (
    generate_cessionarios_pdf, generate_pagamentos_pdf, generate_certidao_pdf, generate_recibos_cobranca_pdf
)
from app.services.excel_service import (
    generate_cessionarios_excel, generate_pagamentos_excel, generate_cobranca_excel
)

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


@router.post("/exportar")
def exportar_relatorio(
    filtros: RelatorioFiltros,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Exporta relatório em PDF ou Excel conforme filtros"""
    
    formato = filtros.formato.lower()
    
    if filtros.tipo == "todos":
        cessionarios, _ = crud_cess.get_cessionarios(db, skip=0, limit=10000)
        if formato == "pdf":
            pdf = generate_cessionarios_pdf(cessionarios, "Relatório Geral de Cessionários")
            return Response(
                content=pdf,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=relatorio_geral.pdf"}
            )
        else:
            excel = generate_cessionarios_excel(cessionarios)
            return Response(
                content=excel,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=relatorio_geral.xlsx"}
            )
    
    elif filtros.tipo == "regulares":
        cessionarios = crud_cess.get_cessionarios_by_situacao(db, Situacao.REGULAR)
        if formato == "pdf":
            pdf = generate_cessionarios_pdf(cessionarios, "Relatório de Cessionários Regulares")
            return Response(content=pdf, media_type="application/pdf",
                          headers={"Content-Disposition": "attachment; filename=regulares.pdf"})
        else:
            excel = generate_cessionarios_excel(cessionarios)
            return Response(content=excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          headers={"Content-Disposition": "attachment; filename=regulares.xlsx"})
    
    elif filtros.tipo == "irregulares":
        cessionarios = crud_cess.get_cessionarios_by_situacao(db, Situacao.IRREGULAR)
        if formato == "pdf":
            pdf = generate_cessionarios_pdf(cessionarios, "Relatório de Cessionários Irregulares")
            return Response(content=pdf, media_type="application/pdf",
                          headers={"Content-Disposition": "attachment; filename=irregulares.pdf"})
        else:
            excel = generate_cessionarios_excel(cessionarios)
            return Response(content=excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          headers={"Content-Disposition": "attachment; filename=irregulares.xlsx"})
    
    elif filtros.tipo == "pagamentos":
        pagamentos, _ = crud_pag.get_pagamentos(
            db, skip=0, limit=10000,
            data_inicio=filtros.data_inicio,
            data_fim=filtros.data_fim
        )
        if formato == "pdf":
            pdf = generate_pagamentos_pdf(pagamentos, "Relatório de Arrecadação")
            return Response(content=pdf, media_type="application/pdf",
                          headers={"Content-Disposition": "attachment; filename=arrecadacao.pdf"})
        else:
            excel = generate_pagamentos_excel(pagamentos)
            return Response(content=excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          headers={"Content-Disposition": "attachment; filename=arrecadacao.xlsx"})
    
    elif filtros.tipo == "cessionarios":
        cessionarios, _ = crud_cess.get_cessionarios(db, skip=0, limit=10000)
        if formato == "pdf":
            pdf = generate_cessionarios_pdf(cessionarios, "Lista de Cessionários")
            return Response(content=pdf, media_type="application/pdf",
                          headers={"Content-Disposition": "attachment; filename=cessionarios.pdf"})
        else:
            excel = generate_cessionarios_excel(cessionarios)
            return Response(content=excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          headers={"Content-Disposition": "attachment; filename=cessionarios.xlsx"})
    
    elif filtros.tipo == "cobranca":
        cessionarios, _ = crud_cess.get_cessionarios(
            db, skip=0, limit=10000, fiscal_id=filtros.fiscal_id
        )
        if formato == "pdf":
            pdf = generate_recibos_cobranca_pdf(cessionarios, filtros.data_cobranca)
            return Response(content=pdf, media_type="application/pdf",
                          headers={"Content-Disposition": "attachment; filename=recibos_cobranca.pdf"})
        else:
            excel = generate_cobranca_excel(cessionarios)
            return Response(content=excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          headers={"Content-Disposition": "attachment; filename=cobranca.xlsx"})
    
    raise HTTPException(status_code=400, detail="Tipo de relatório inválido")


@router.get("/certidao/{cessionario_id}")
def gerar_certidao(
    cessionario_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Gera certidão de situação em PDF"""
    cessionario = crud_cess.get_cessionario(db, cessionario_id)
    if not cessionario:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    
    pdf = generate_certidao_pdf(cessionario)
    filename = f"certidao_{cessionario.nome.replace(' ', '_').lower()}.pdf"
    
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
