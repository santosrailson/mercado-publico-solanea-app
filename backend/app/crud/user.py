from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.models import User, UserStatus, UserRole
from app.schemas.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(func.lower(User.email) == func.lower(email)).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[UserStatus] = None
) -> List[User]:
    query = db.query(User)
    if status:
        query = query.filter(User.status == status)
    return query.offset(skip).limit(limit).all()


def get_pending_users_count(db: Session) -> int:
    return db.query(User).filter(User.status == UserStatus.PENDING).count()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        nome=user.nome,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        status=UserStatus.ACTIVE
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if user.status != UserStatus.ACTIVE:
        return None
    return user


def approve_user(db: Session, user_id: int) -> Optional[User]:
    return update_user(db, user_id, UserUpdate(status=UserStatus.ACTIVE))
