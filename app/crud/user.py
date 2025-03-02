from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, PasswordUpdate
from app.core.security import hash_password, verify_password
from typing import Optional, List
from uuid import UUID

def create_user(db: Session, user: UserCreate) -> User:
    try:
        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            address=user.address
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
def delete_user(db: Session, user_id: UUID) -> None:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
def update_user_password(db: Session, user_id: UUID, current_password: str, new_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Verificar la contraseña actual
    if not verify_password(current_password, user.hashed_password):  # Implementa verify_password
        raise ValueError("Contraseña actual incorrecta.")

    # Actualizar la contraseña
    hashed_password = hash_password(new_password)
    user.hashed_password = hashed_password
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: UUID, user_in: UserUpdate) -> Optional[User]:
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if user_in.password and user_in.password.strip() != "":
            user_in.password = hash_password(user_in.password)
        update_data = user_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user,key, value)
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    
def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db:Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_phone(db:Session, phone: str) -> User:
    return db.query(User).filter(User.phone == phone).first()

def get_user_by_name(db:Session, name: str) -> List[User]:
    return db.query(User).filter(or_(User.first_name.ilike(f"%{name}%"), User.last_name.ilike(f"%{name}%"))).all()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()