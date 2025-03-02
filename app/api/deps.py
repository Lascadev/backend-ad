from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import settings
from app.core.security import oauth2_scheme, decode_access_token
from app.models.user import User
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verificar si el token es None o vacío antes de decodificarlo
    if not token:
        raise credentials_exception

    try:
        # Intentar decodificar el token
        payload = decode_access_token(token)

        # Si el payload es None, lanzar excepción
        if payload is None:
            raise credentials_exception

        # Verificar si el "sub" está presente en el payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

    except JWTError as e:
        # Aquí puedes capturar cualquier error de decodificación del JWT y proporcionar más detalles
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: " + str(e))

    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario Inactivo")
    return current_user