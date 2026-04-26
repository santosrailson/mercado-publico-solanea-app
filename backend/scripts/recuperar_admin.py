"""
Script de emergência: recupera o acesso do admin.
Redefine o usuário admin para status ativo, role admin e senha padrão.
Execute dentro do container backend:
    python scripts/recuperar_admin.py
"""

import sqlite3
import os
import sys

# Adiciona o path para importar os módulos do app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.crud import user as crud_user


def recuperar_admin():
    db = SessionLocal()
    try:
        admin = crud_user.get_user_by_email(db, "admin@mercado.pb.gov.br")
        
        if not admin:
            print("❌ Admin não encontrado. Criando novo admin...")
            from app.models.models import User, UserRole, UserStatus
            admin = User(
                nome="Administrador",
                email="admin@mercado.pb.gov.br",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            db.add(admin)
            db.commit()
            print("✅ Admin criado:")
        else:
            from app.models.models import UserRole, UserStatus
            admin.role = UserRole.ADMIN
            admin.status = UserStatus.ACTIVE
            admin.hashed_password = get_password_hash("admin123")
            db.commit()
            db.refresh(admin)
            print("✅ Admin recuperado:")
        
        print("   Email: admin@mercado.pb.gov.br")
        print("   Senha: admin123")
        print("   Role: ADMIN")
        print("   Status: ACTIVE")
        
    finally:
        db.close()


if __name__ == "__main__":
    recuperar_admin()
