from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from app.models.models import UserRole, UserStatus, Situacao, Periodicidade


# ============== USER SCHEMAS ==============

class UserBase(BaseModel):
    nome: str
    email: str
    role: UserRole = UserRole.OPERATOR


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: UserStatus
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============== CESSIONÁRIO SCHEMAS ==============

class CessionarioBase(BaseModel):
    nome: str
    numero_box: Optional[str] = None
    atividade: Optional[str] = None
    telefone: Optional[str] = None
    situacao: Situacao = Situacao.REGULAR
    valor_referencia: float = 0.0
    periodicidade_referencia: Periodicidade = Periodicidade.MENSAL
    observacoes: Optional[str] = None


class CessionarioCreate(CessionarioBase):
    pass


class CessionarioUpdate(BaseModel):
    nome: Optional[str] = None
    numero_box: Optional[str] = None
    atividade: Optional[str] = None
    telefone: Optional[str] = None
    situacao: Optional[Situacao] = None
    valor_referencia: Optional[float] = None
    periodicidade_referencia: Optional[Periodicidade] = None
    observacoes: Optional[str] = None


class CessionarioResponse(CessionarioBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
    ultimo_pagamento: Optional[datetime] = None


class CessionarioDetailResponse(CessionarioResponse):
    pagamentos: List["PagamentoResponse"] = []


class CessionarioListFilters(BaseModel):
    search: Optional[str] = None
    situacao: Optional[Situacao] = None
    atividade: Optional[str] = None
    skip: int = 0
    limit: int = 20


# ============== PAGAMENTO SCHEMAS ==============

class PagamentoBase(BaseModel):
    valor: float
    data_pagamento: datetime
    periodicidade: Periodicidade
    referencia_mes: Optional[str] = None
    observacoes: Optional[str] = None


class PagamentoCreate(PagamentoBase):
    cessionario_id: int


class PagamentoUpdate(BaseModel):
    valor: Optional[float] = None
    data_pagamento: Optional[datetime] = None
    periodicidade: Optional[Periodicidade] = None
    referencia_mes: Optional[str] = None
    observacoes: Optional[str] = None


class PagamentoResponse(PagamentoBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    cessionario_id: int
    cessionario_nome: Optional[str] = None
    registrado_por_nome: Optional[str] = None
    created_at: datetime


class PagamentoListFilters(BaseModel):
    search: Optional[str] = None
    periodicidade: Optional[Periodicidade] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    skip: int = 0
    limit: int = 20


# ============== DASHBOARD SCHEMAS ==============

class DashboardKPIs(BaseModel):
    total_cessionarios: int
    total_regulares: int
    total_irregulares: int
    total_pagamentos_mes: float
    total_pagamentos_semana: float


class ChartData(BaseModel):
    labels: List[str]
    values: List[float]


class DashboardData(BaseModel):
    kpis: DashboardKPIs
    arrecadacao_mensal: ChartData
    situacao_chart: ChartData
    top_cessionarios: List[dict]
    atividades_recentes: List[dict]


# ============== RELATÓRIO SCHEMAS ==============

class RelatorioFiltros(BaseModel):
    tipo: str  # todos, regulares, irregulares, pagamentos, cobranca, cessionarios
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    data_referencia: Optional[date] = None
    data_cobranca: Optional[date] = None
    formato: str = "pdf"  # pdf, excel


# ============== CERTIDÃO SCHEMAS ==============

class CertidaoRequest(BaseModel):
    cessionario_id: int
    data_referencia: Optional[datetime] = None


class CertidaoResponse(BaseModel):
    cessionario_nome: str
    numero_box: Optional[str]
    situacao: Situacao
    data_emissao: datetime
    data_referencia: datetime
    hash_verificacao: str
