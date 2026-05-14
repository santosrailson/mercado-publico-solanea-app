from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.models import User, UserRole, UserStatus

def test_login_success(client: TestClient, db: Session):
    # Criar usuário de teste
    test_user = User(
        nome="Teste",
        email="teste@solanea.pb.gov.br",
        hashed_password=get_password_hash("senha123"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    db.add(test_user)
    db.commit()

    # Tentar login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "teste@solanea.pb.gov.br", "password": "senha123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "teste@solanea.pb.gov.br"

def test_login_invalid_password(client: TestClient, db: Session):
    # Criar usuário de teste
    test_user = User(
        nome="Teste 2",
        email="teste2@solanea.pb.gov.br",
        hashed_password=get_password_hash("senha123"),
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    db.add(test_user)
    db.commit()

    # Tentar login com senha errada
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "teste2@solanea.pb.gov.br", "password": "senhaerrada"}
    )
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha incorretos"
