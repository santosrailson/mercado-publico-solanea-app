from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime, date
from typing import List, Optional

from app.models.models import Cessionario, Pagamento, Situacao


def generate_cessionarios_pdf(cessionarios: List[Cessionario], titulo: str = "Relatório de Cessionários") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#00a87a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    elements.append(Paragraph(titulo, title_style))
    elements.append(Paragraph(f"Emitido em: {datetime.now(ZoneInfo('America/Recife')).strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Tabela
    data = [['Nome', 'Box/Ponto', 'Atividade', 'Situação', 'Valor Ref.']]
    
    for c in cessionarios:
        data.append([
            c.nome,
            c.numero_box or '-',
            c.atividade or '-',
            c.situacao.value,
            f"R$ {c.valor_referencia:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ])
    
    table = Table(data, colWidths=[7*cm, 2.5*cm, 3.5*cm, 2.5*cm, 2.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00a87a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Resumo
    total_regulares = sum(1 for c in cessionarios if c.situacao == Situacao.REGULAR)
    total_irregulares = sum(1 for c in cessionarios if c.situacao == Situacao.IRREGULAR)
    
    elements.append(Paragraph(f"<b>Resumo:</b>", styles['Normal']))
    elements.append(Paragraph(f"Total: {len(cessionarios)} cessionários", styles['Normal']))
    elements.append(Paragraph(f"Regulares: {total_regulares}", styles['Normal']))
    elements.append(Paragraph(f"Irregulares: {total_irregulares}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def generate_recibos_cobranca_pdf(cessionarios: List[Cessionario], data_cobranca: Optional[date] = None) -> bytes:
    """Gera PDF de recibos de cobrança com duas vias, 8 recibos por folha (4 cessionários)."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Cores
    COR_PRIMARIA = colors.HexColor('#00a87a')
    COR_CINZA = colors.HexColor('#f5f5f5')
    COR_TEXTO = colors.HexColor('#333333')
    COR_BORDA = colors.HexColor('#cccccc')

    # Configurações de layout (em mm)
    margem = 8 * mm
    gap_h = 6 * mm
    gap_v = 5 * mm
    recibo_w = (width - 2 * margem - gap_h) / 2
    recibo_h = (height - 2 * margem - 3 * gap_v) / 4

    data_str = data_cobranca.strftime('%d/%m/%Y') if data_cobranca else datetime.now(ZoneInfo('America/Recife')).strftime('%d/%m/%Y')

    def draw_recibo(x, y, cessionario, via):
        """Desenha um único recibo na posição (x, y) canto inferior esquerdo."""
        # Fundo branco com borda suave
        c.setFillColor(colors.white)
        c.setStrokeColor(COR_BORDA)
        c.setLineWidth(0.5)
        c.rect(x, y, recibo_w, recibo_h, fill=1, stroke=1)

        # Cabeçalho com cor primária
        header_h = 10 * mm
        c.setFillColor(COR_PRIMARIA)
        c.rect(x, y + recibo_h - header_h, recibo_w, header_h, fill=1, stroke=0)

        # Título no cabeçalho
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 4*mm, y + recibo_h - 6.5*mm, "RECIBO DE COBRANÇA")

        # Via no canto direito do cabeçalho
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(x + recibo_w - 4*mm, y + recibo_h - 6.5*mm, via)
        c.setFillColor(COR_TEXTO)

        # Dados do cessionário - layout em duas colunas internas
        left_col = x + 4*mm
        right_col = x + recibo_w / 2 + 2*mm
        line_y = y + recibo_h - 14*mm

        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(left_col, line_y, "Cessionário:")
        c.setFont("Helvetica", 7.5)
        nome_truncado = cessionario.nome[:32] + "..." if len(cessionario.nome) > 35 else cessionario.nome
        c.drawString(left_col + 22*mm, line_y, nome_truncado)

        line_y -= 5.5*mm
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(left_col, line_y, "Box/Ponto:")
        c.setFont("Helvetica", 7.5)
        c.drawString(left_col + 22*mm, line_y, cessionario.numero_box or '-')

        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(right_col, line_y, "Ativ.:")
        c.setFont("Helvetica", 7.5)
        ativ_truncada = (cessionario.atividade or '-')[:14]
        c.drawString(right_col + 12*mm, line_y, ativ_truncada)

        line_y -= 5.5*mm
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(left_col, line_y, "Periodicidade:")
        c.setFont("Helvetica", 7.5)
        periodicidade_str = cessionario.periodicidade_referencia.value if cessionario.periodicidade_referencia else '-'
        c.drawString(left_col + 22*mm, line_y, periodicidade_str)

        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(right_col, line_y, "Valor:")
        c.setFont("Helvetica", 7.5)
        valor_str = f"R$ {cessionario.valor_referencia:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        c.drawString(right_col + 12*mm, line_y, valor_str)

        line_y -= 5.5*mm
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(left_col, line_y, "Data Cobrança:")
        c.setFont("Helvetica", 7.5)
        c.drawString(left_col + 22*mm, line_y, data_str)

        # Texto de declaração
        line_y -= 6*mm
        c.setFont("Helvetica-Oblique", 6.5)
        c.setFillColor(colors.HexColor('#666666'))
        decl = "Declaro que recebi a notificação de cobrança referente ao período acima."
        c.drawCentredString(x + recibo_w / 2, line_y, decl)
        c.setFillColor(COR_TEXTO)

        # Linhas de assinatura
        line_y -= 8*mm
        c.setStrokeColor(colors.HexColor('#999999'))
        c.setLineWidth(0.5)

        # Assinatura Fiscal
        c.line(left_col, line_y, left_col + 32*mm, line_y)
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(left_col + 16*mm, line_y - 3*mm, "Fiscal Responsável")

        # Carimbo/Data
        c.line(right_col + 8*mm, line_y, right_col + 40*mm, line_y)
        c.drawCentredString(right_col + 24*mm, line_y - 3*mm, "Carimbo / Data")

        # Rodapé com identificação
        c.setFont("Helvetica", 5.5)
        c.setFillColor(colors.HexColor('#999999'))
        c.drawCentredString(x + recibo_w / 2, y + 2.5*mm, "MERCADO PÚBLICO DE SOLÂNEA - PB")
        c.setFillColor(COR_TEXTO)

    def draw_cut_lines(page_cessionarios):
        """Desenha linhas tracejadas de corte entre todos os recibos da página."""
        c.setDash(2, 2)
        c.setStrokeColor(colors.HexColor('#bbbbbb'))
        c.setLineWidth(0.4)

        # Linha vertical no meio (separando colunas)
        mid_x = margem + recibo_w + gap_h / 2
        c.line(mid_x, margem - 3*mm, mid_x, height - margem + 3*mm)

        # Linhas horizontais (separando linhas)
        for row in range(1, 4):
            mid_y = margem + (4 - row) * recibo_h + (4 - row - 0.5) * gap_v
            c.line(margem - 3*mm, mid_y, width - margem + 3*mm, mid_y)

        c.setDash()
        c.setStrokeColor(colors.black)

    # Processa cessionários em grupos de 4 (4 cessionários por folha = 8 recibos)
    for i in range(0, len(cessionarios), 4):
        grupo = cessionarios[i:i+4]

        # Desenha linhas de corte
        draw_cut_lines(grupo)

        for row, cess in enumerate(grupo):
            # Posição Y (de cima para baixo)
            y = height - margem - (row + 1) * recibo_h - row * gap_v

            # 1ª via (coluna esquerda)
            x1 = margem
            draw_recibo(x1, y, cess, "1ª VIA")

            # 2ª via (coluna direita)
            x2 = margem + recibo_w + gap_h
            draw_recibo(x2, y, cess, "2ª VIA")

        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def generate_pagamentos_pdf(pagamentos: List[Pagamento], titulo: str = "Relatório de Pagamentos") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#00a87a'),
        spaceAfter=30,
        alignment=1
    )
    
    elements.append(Paragraph(titulo, title_style))
    elements.append(Paragraph(f"Emitido em: {datetime.now(ZoneInfo('America/Recife')).strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    data = [['Cessionário', 'Data', 'Periodicidade', 'Referência', 'Valor']]
    total = 0.0
    
    for p in pagamentos:
        data.append([
            p.cessionario.nome if p.cessionario else '-',
            p.data_pagamento.strftime('%d/%m/%Y'),
            p.periodicidade.value,
            p.referencia_mes or '-',
            f"R$ {p.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ])
        total += p.valor
    
    table = Table(data, colWidths=[6*cm, 2.5*cm, 3*cm, 2.5*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00a87a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"<b>Total Arrecadado: R$ {total:,.2f}</b>".replace(',', 'X').replace('.', ',').replace('X', '.'), styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


import random
import string
from zoneinfo import ZoneInfo

def _generate_certidao_code() -> str:
    """Gera código alfanumérico único de verificação do documento."""
    parts = [
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        for _ in range(3)
    ]
    return f"SOL-{parts[0]}-{parts[1]}-{parts[2]}"


def generate_certidao_pdf(cessionario: Cessionario, data_emissao: datetime = None) -> tuple[bytes, str]:
    """Gera certidão de situação profissional com código de verificação.
    Retorna (pdf_bytes, codigo_verificacao)
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Cores institucionais
    COR_PRIMARIA = colors.HexColor('#00a87a')
    COR_DOURADO = colors.HexColor('#b8860b')
    COR_CINZA = colors.HexColor('#f8f9fa')
    COR_TEXTO = colors.HexColor('#2c3e50')
    COR_BORDA = colors.HexColor('#bdc3c7')

    codigo = _generate_certidao_code()
    if data_emissao is None:
        data_emissao = datetime.now(ZoneInfo('America/Recife'))
    data_emissao_str = data_emissao.strftime('%d/%m/%Y')
    hora_emissao = data_emissao.strftime('%H:%M')

    # Margens e área útil
    margem = 2.5 * cm
    inner_w = width - 2 * margem
    inner_h = height - 2 * margem
    x = margem
    y = margem

    # Fundo com borda decorativa dupla
    c.setFillColor(colors.white)
    c.setStrokeColor(COR_PRIMARIA)
    c.setLineWidth(2)
    c.rect(x, y, inner_w, inner_h, fill=1, stroke=1)

    c.setStrokeColor(COR_DOURADO)
    c.setLineWidth(0.5)
    c.rect(x + 8, y + 8, inner_w - 16, inner_h - 16, fill=0, stroke=1)

    # Cabeçalho institucional
    header_y = height - margem - 1.2*cm
    c.setFillColor(COR_PRIMARIA)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, header_y, "PREFEITURA MUNICIPAL DE SOLÂNEA")
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, header_y - 14, "ESTADO DA PARAÍBA")
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, header_y - 30, "MERCADO PÚBLICO MUNICIPAL WALDOMIRO JAYME DA ROCHA")
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2, header_y - 46, "Lei Municipal nº 014/2021, de 05 de Maio de 2021")

    # Título do documento
    title_y = header_y - 80
    c.setFillColor(COR_PRIMARIA)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, title_y, "CERTIDÃO DE SITUAÇÃO CADASTRAL")

    # Linha decorativa sob o título
    c.setStrokeColor(COR_DOURADO)
    c.setLineWidth(1.5)
    c.line(width / 2 - 120, title_y - 8, width / 2 + 120, title_y - 8)

    # Código de verificação em destaque (caixa)
    code_y = title_y - 45
    code_w = 220
    code_h = 28
    code_x = width / 2 - code_w / 2
    c.setFillColor(COR_CINZA)
    c.setStrokeColor(COR_PRIMARIA)
    c.setLineWidth(0.8)
    c.roundRect(code_x, code_y, code_w, code_h, 5, fill=1, stroke=1)
    c.setFillColor(COR_TEXTO)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(width / 2, code_y + 17, "CÓDIGO DE VERIFICAÇÃO")
    c.setFont("Courier-Bold", 11)
    c.setFillColor(COR_PRIMARIA)
    c.drawCentredString(width / 2, code_y + 5, codigo)

    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import ParagraphStyle

    # Texto de certificação (no lugar do antigo texto introdutório)
    text_y = code_y - 35
    c.setFillColor(COR_TEXTO)
    c.setFont("Times-Roman", 10)

    texto_cert = (
        f"Certifica-se, portanto, que o(a) acima qualificado(a) encontra-se com situação "
        f"<b>{cessionario.situacao.value.upper()}</b> no cadastro do Mercado Público Municipal, "
        f"estando em gozo de todos os direitos e obrigações inerentes ao uso do espaço público "
        f"concedido, nos termos da legislação vigente."
    )

    intro_style = ParagraphStyle(
        'Intro',
        fontName='Times-Roman',
        fontSize=10,
        leading=15,
        alignment=4,  # Justified
        textColor=COR_TEXTO
    )
    p_intro = Paragraph(texto_cert, intro_style)
    p_intro.wrapOn(c, inner_w - 60, 120)
    p_intro.drawOn(c, x + 30, text_y - p_intro.height + 15)

    # Bloco de dados do cessionário
    block_y = text_y - p_intro.height - 30
    block_h = 145
    c.setFillColor(COR_CINZA)
    c.setStrokeColor(COR_BORDA)
    c.roundRect(x + 30, block_y - block_h + 10, inner_w - 60, block_h, 4, fill=1, stroke=1)

    c.setFillColor(COR_TEXTO)
    dados = [
        ("Nome:", cessionario.nome),
        ("Box / Ponto:", cessionario.numero_box or 'N/A'),
        ("Atividade:", cessionario.atividade or 'N/A'),
        ("Situação:", cessionario.situacao.value.upper()),
        ("Periodicidade:", cessionario.periodicidade_referencia.value if cessionario.periodicidade_referencia else 'N/A'),
        ("Valor Referência:", f"R$ {cessionario.valor_referencia:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')),
    ]

    line_h = block_y - 15
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COR_PRIMARIA)
    c.drawString(x + 45, line_h, "DADOS DO CESSIONÁRIO")
    line_h -= 20

    c.setFillColor(COR_TEXTO)
    for label, value in dados:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 45, line_h, label)
        c.setFont("Helvetica", 9)
        c.drawString(x + 130, line_h, str(value))
        line_h -= 14

    # Data e local
    data_y = block_y - block_h - 25
    c.setFont("Times-Roman", 10)
    c.drawCentredString(width / 2, data_y, f"Solânea - PB, {data_emissao_str} às {hora_emissao}")

    # Selo de autenticação digital
    ass_y = data_y - 70
    selo_w = 160
    selo_h = 52
    selo_x = width / 2 - selo_w / 2

    # Borda verde do selo (sem fundo)
    c.setFillColor(colors.white)
    c.setStrokeColor(COR_PRIMARIA)
    c.setLineWidth(1.5)
    c.roundRect(selo_x, ass_y - selo_h / 2, selo_w, selo_h, 5, fill=1, stroke=1)

    # Texto verde no selo (distribuído simetricamente)
    c.setFillColor(COR_PRIMARIA)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, ass_y + 10, "✓  AUTENTICADO")
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, ass_y, "Documento verificado eletronicamente")
    c.drawCentredString(width / 2, ass_y - 10, f"Código: {codigo}")

    # Rodapé com validação
    footer_y = margem + 25
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(width / 2, footer_y, f"Este documento é válido mediante verificação do código {codigo} junto à Administração do Mercado Público.")
    c.drawCentredString(width / 2, footer_y - 10, "Qualquer alteração invalida o presente documento.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue(), codigo
