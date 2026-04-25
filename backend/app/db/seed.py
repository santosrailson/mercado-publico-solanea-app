"""
Script para criar dados iniciais no banco.
Execute: python -m app.db.seed
"""

from app.db.database import SessionLocal, engine
from app.models.models import Base, User, UserRole, UserStatus
from app.core.security import get_password_hash


def seed_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Verifica se já existe usuário admin
        admin = db.query(User).filter(User.email == "admin@mercado.pb.gov.br").first()
        
        if not admin:
            admin = User(
                nome="Administrador",
                email="admin@mercado.pb.gov.br",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            db.add(admin)
            db.commit()
            print("✅ Usuário admin criado:")
            print("   Email: admin@mercado.pb.gov.br")
            print("   Senha: admin123")
        else:
            print("ℹ️ Usuário admin já existe")
            
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
