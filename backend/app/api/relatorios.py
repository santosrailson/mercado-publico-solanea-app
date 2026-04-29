from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.models.models import Situacao, UserRole, User
from app.schemas.schemas import RelatorioFiltros, CertidaoVerificacaoResponse
from app.crud import cessionario as crud_cess
from app.crud import pagamento as crud_pag
from app.crud import certidao as crud_cert
from app.crud import user as crud_user
from app.services.pdf_service import (
    generate_cessionarios_pdf, generate_pagamentos_pdf, generate_certidao_pdf, generate_recibos_cobranca_pdf
)
from app.services.excel_service import (
    generate_cessionarios_excel, generate_pagamentos_excel, generate_cobranca_excel
)

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


def get_current_user(db: Session, user_id: int) -> User:
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


def get_fiscal_filter(user: User) -> Optional[int]:
    """Retorna fiscal_id se o usuário for um fiscal (não admin)"""
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        return user.fiscal_id
    return None


@router.post("/exportar")
def exportar_relatorio(
    filtros: RelatorioFiltros,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Exporta relatório em PDF ou Excel conforme filtros"""
    
    user = get_current_user(db, current_user_id)
    fiscal_filter = get_fiscal_filter(user)
    
    # Se for fiscal, sobrescreve o fiscal_id do filtro
    if fiscal_filter is not None:
        filtros.fiscal_id = fiscal_filter
    
    formato = filtros.formato.lower()
    
    if filtros.tipo == "todos":
        cessionarios, _ = crud_cess.get_cessionarios(
            db, skip=0, limit=10000, fiscal_id=filtros.fiscal_id
        )
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
        cessionarios, _ = crud_cess.get_cessionarios(
            db, skip=0, limit=10000, situacao=Situacao.REGULAR, fiscal_id=filtros.fiscal_id
        )
        if formato == "pdf":
            pdf = generate_cessionarios_pdf(cessionarios, "Relatório de Cessionários Regulares")
            return Response(content=pdf, media_type="application/pdf",
                          headers={"Content-Disposition": "attachment; filename=regulares.pdf"})
        else:
            excel = generate_cessionarios_excel(cessionarios)
            return Response(content=excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          headers={"Content-Disposition": "attachment; filename=regulares.xlsx"})
    
    elif filtros.tipo == "irregulares":
        cessionarios, _ = crud_cess.get_cessionarios(
            db, skip=0, limit=10000, situacao=Situacao.IRREGULAR, fiscal_id=filtros.fiscal_id
        )
        if formato == "pdf":
            pdf = generate_cessionarios_pdf(cessionarios, "Relatório de Cessionários Irregulares")
            return Response(content=pdf, media_type="application/pdf",
                          headers={"Content-Disposition": "attachment; filename=irregulares.pdf"})
        else:
            excel = generate_cessionarios_excel(cessionarios)
            return Response(content=excel, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                          headers={"Content-Disposition": "attachment; filename=irregulares.xlsx"})
    
    elif filtros.tipo == "pagamentos":
        # Para pagamentos, precisamos filtrar por cessionários do fiscal
        if fiscal_filter is not None:
            cessionarios, _ = crud_cess.get_cessionarios(
                db, skip=0, limit=10000, fiscal_id=fiscal_filter
            )
            cessionario_ids = [c.id for c in cessionarios]
            pagamentos, _ = crud_pag.get_pagamentos(
                db, skip=0, limit=10000,
                data_inicio=filtros.data_inicio,
                data_fim=filtros.data_fim,
                cessionario_ids=cessionario_ids
            )
        else:
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
        cessionarios, _ = crud_cess.get_cessionarios(
            db, skip=0, limit=10000, fiscal_id=filtros.fiscal_id
        )
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
            import random, string
            parts = [
                ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
                for _ in range(2)
            ]
            codigo_controle = f"RCB-{parts[0]}-{parts[1]}"
            pdf = generate_recibos_cobranca_pdf(cessionarios, filtros.data_cobranca, codigo_controle)
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
    """Gera certidão de situação em PDF e registra no banco"""
    user = get_current_user(db, current_user_id)
    
    cessionario = crud_cess.get_cessionario(db, cessionario_id)
    if not cessionario:
        raise HTTPException(status_code=404, detail="Cessionário não encontrado")
    
    # Verifica se fiscal pode gerar certidão para este cessionário
    if user.role != UserRole.ADMIN and user.fiscal_id is not None:
        if cessionario.fiscal_id != user.fiscal_id:
            raise HTTPException(status_code=403, detail="Você não tem permissão para gerar certidão deste cessionário")
    
    agora = datetime.now(ZoneInfo('America/Recife'))
    data_validade = agora + timedelta(days=90)
    pdf, codigo = generate_certidao_pdf(cessionario, data_emissao=agora)
    
    # Salva a certidão no banco para verificação futura
    crud_cert.create_certidao(
        db,
        cessionario_id=cessionario_id,
        codigo=codigo,
        data_emissao=agora,
        data_validade=data_validade
    )
    
    filename = f"certidao_{cessionario.nome.replace(' ', '_').lower()}.pdf"
    
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/verificar-certidao/{codigo}", response_model=CertidaoVerificacaoResponse)
def verificar_certidao(
    codigo: str,
    db: Session = Depends(get_db)
):
    """Verifica a autenticidade de uma certidão pelo código (público, sem login)"""
    certidao = crud_cert.get_certidao_by_codigo(db, codigo)
    
    if not certidao:
        return CertidaoVerificacaoResponse(
            valido=False,
            mensagem="Código de verificação não encontrado. Documento pode ser fraudulento."
        )
    
    agora = datetime.now(ZoneInfo('America/Recife'))
    if certidao.data_validade and agora > certidao.data_validade:
        return CertidaoVerificacaoResponse(
            valido=False,
            mensagem=f"Certidão expirada em {certidao.data_validade.strftime('%d/%m/%Y')}. Solicite uma nova certidão.",
            cessionario_nome=certidao.cessionario.nome if certidao.cessionario else None,
            numero_box=certidao.cessionario.numero_box if certidao.cessionario else None,
            situacao=certidao.cessionario.situacao.value if certidao.cessionario else None,
            data_emissao=certidao.data_emissao,
            data_validade=certidao.data_validade,
            codigo=certidao.codigo
        )
    
    return CertidaoVerificacaoResponse(
        valido=True,
        mensagem="Certidão verificada com sucesso. Documento autêntico.",
        cessionario_nome=certidao.cessionario.nome if certidao.cessionario else None,
        numero_box=certidao.cessionario.numero_box if certidao.cessionario else None,
        situacao=certidao.cessionario.situacao.value if certidao.cessionario else None,
        data_emissao=certidao.data_emissao,
        data_validade=certidao.data_validade,
        codigo=certidao.codigo
    )
