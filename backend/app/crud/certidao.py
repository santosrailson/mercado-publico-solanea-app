from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.models import Certidao


def get_certidao_by_codigo(db: Session, codigo: str) -> Optional[Certidao]:
    return db.query(Certidao).filter(Certidao.codigo == codigo).first()


def create_certidao(
    db: Session,
    cessionario_id: int,
    codigo: str,
    data_emissao: datetime,
    data_referencia: Optional[datetime] = None,
    data_validade: Optional[datetime] = None
) -> Certidao:
    db_certidao = Certidao(
        cessionario_id=cessionario_id,
        codigo=codigo,
        data_emissao=data_emissao,
        data_referencia=data_referencia,
        data_validade=data_validade
    )
    db.add(db_certidao)
    db.commit()
    db.refresh(db_certidao)
    return db_certidao
