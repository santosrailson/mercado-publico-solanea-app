from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base


class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class Situacao(str, enum.Enum):
    REGULAR = "Regular"
    IRREGULAR = "Irregular"


class Periodicidade(str, enum.Enum):
    MENSAL = "Mensal"
    SEMANAL = "Semanal"
    QUINZENAL = "Quinzenal"
    UNICO = "Único"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.OPERATOR)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pagamentos_registrados = relationship("Pagamento", back_populates="registrado_por")


class Fiscal(Base):
    __tablename__ = "fiscais"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    matricula = Column(String(50), nullable=True, unique=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cessionarios = relationship("Cessionario", back_populates="fiscal")


class Cessionario(Base):
    __tablename__ = "cessionarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    numero_box = Column(String(50), nullable=True)
    atividade = Column(String(100), nullable=True)
    telefone = Column(String(20), nullable=True)
    situacao = Column(Enum(Situacao), default=Situacao.REGULAR)
    valor_referencia = Column(Float, default=0.0)
    periodicidade_referencia = Column(Enum(Periodicidade), default=Periodicidade.MENSAL)
    observacoes = Column(Text, nullable=True)
    fiscal_id = Column(Integer, ForeignKey("fiscais.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pagamentos = relationship("Pagamento", back_populates="cessionario", cascade="all, delete-orphan")
    fiscal = relationship("Fiscal", back_populates="cessionarios")


class Pagamento(Base):
    __tablename__ = "pagamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    cessionario_id = Column(Integer, ForeignKey("cessionarios.id"), nullable=False)
    valor = Column(Float, nullable=False)
    data_pagamento = Column(DateTime, nullable=False)
    periodicidade = Column(Enum(Periodicidade), nullable=False)
    referencia_mes = Column(String(20), nullable=True)  # ex: "01/2024"
    observacoes = Column(Text, nullable=True)
    registrado_por_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cessionario = relationship("Cessionario", back_populates="pagamentos")
    registrado_por = relationship("User", back_populates="pagamentos_registrados")


class Certidao(Base):
    __tablename__ = "certidoes"
    
    id = Column(Integer, primary_key=True, index=True)
    cessionario_id = Column(Integer, ForeignKey("cessionarios.id"), nullable=False)
    codigo = Column(String(50), nullable=False, unique=True, index=True)
    data_emissao = Column(DateTime, nullable=False)
    data_referencia = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cessionario = relationship("Cessionario")
