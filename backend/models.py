from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ── Auth ────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    nome: str
    is_admin: bool
    aprovado: bool


# ── Users ───────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    nome: str
    email: str
    senha: str
    is_admin: bool = False


class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
    is_admin: Optional[bool] = None
    aprovado: Optional[bool] = None


class UserOut(BaseModel):
    id: str
    nome: str
    email: str
    is_admin: bool
    aprovado: bool
    criado_por: Optional[str] = None
    criado_em: Optional[str] = None


# ── Cessionários ────────────────────────────────────────────────────────────

class CessionarioCreate(BaseModel):
    nome: str
    numero_box: Optional[str] = None
    atividade: Optional[str] = None
    telefone: Optional[str] = None
    situacao: str = "Regular"
    valor_ref: float = 0.0
    per_ref: str = "Mensal"
    observacao: Optional[str] = None


class CessionarioUpdate(BaseModel):
    nome: Optional[str] = None
    numero_box: Optional[str] = None
    atividade: Optional[str] = None
    telefone: Optional[str] = None
    situacao: Optional[str] = None
    valor_ref: Optional[float] = None
    per_ref: Optional[str] = None
    observacao: Optional[str] = None


class CessionarioOut(BaseModel):
    id: str
    nome: str
    numero_box: Optional[str] = None
    atividade: Optional[str] = None
    telefone: Optional[str] = None
    situacao: str
    valor_ref: float
    per_ref: str
    observacao: Optional[str] = None
    criado_por: Optional[str] = None
    criado_em: Optional[str] = None
    cadastrador_nome: Optional[str] = None
    total_pago: float = 0.0
    ultimo_pagamento: Optional[str] = None


# ── Pagamentos ──────────────────────────────────────────────────────────────

class PagamentoCreate(BaseModel):
    cessionario_id: str
    data: str
    valor: float
    periodicidade: str = "Mensal"
    observacao: Optional[str] = None

    @field_validator("valor")
    @classmethod
    def valor_positivo(cls, v):
        if v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v


class PagamentoUpdate(BaseModel):
    cessionario_id: Optional[str] = None
    data: Optional[str] = None
    valor: Optional[float] = None
    periodicidade: Optional[str] = None
    observacao: Optional[str] = None

    @field_validator("valor")
    @classmethod
    def valor_positivo(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Valor deve ser maior que zero")
        return v


class PagamentoOut(BaseModel):
    id: str
    cessionario_id: str
    data: str
    valor: float
    periodicidade: str
    observacao: Optional[str] = None
    usuario_id: Optional[str] = None
    criado_em: Optional[str] = None
    cessionario_nome: Optional[str] = None
    cessionario_box: Optional[str] = None
    usuario_nome: Optional[str] = None


# ── Dashboard ───────────────────────────────────────────────────────────────

class GraficoMes(BaseModel):
    mes: str
    total: float


class TopPagador(BaseModel):
    id: str
    nome: str
    total: float


class AtividadeRecente(BaseModel):
    tipo: str
    descricao: str
    data: str
    usuario: Optional[str] = None


class DashStats(BaseModel):
    total_cess: int
    regulares: int
    irregulares: int
    total_arrecadado: float
    total_pagamentos: int
    pagamentos_mensais: float
    grafico_6meses: List[GraficoMes]
    top_pagadores: List[TopPagador]
    atividade_recente: List[AtividadeRecente]


# ── Certidão ─────────────────────────────────────────────────────────────────

class CertidaoResponse(BaseModel):
    numero: str
    cessionario: str
    numero_box: Optional[str] = None
    atividade: Optional[str] = None
    situacao: str
    ausencias: List[str]
    ultimo_pagamento: Optional[str] = None
    periodicidade: str
    emitido_em: str
    emitido_por: str
    total_pago: float
    valor_ref: float
