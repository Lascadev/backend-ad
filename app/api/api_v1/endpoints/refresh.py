from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_db
from app.core.security import decode_refresh_token, validate_refresh_token, create_access_token, create_refresh_token
from app.crud.user import get_user_by_email
from app.models import User
from app.schemas.token import Token
from app.schemas.user import UserOut
from app.core.config import settings
from jose import JWTError, ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

@router.post("/")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        # Decodificar el refresh token
        payload = decode_refresh_token(refresh_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Validar que el usuario exista
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Crear un nuevo access_token
        access_token_expires = timedelta(minutes=30)  # Establece el tiempo de expiración
        new_access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        new_refresh_token = create_refresh_token(data={"sub": user.email})  # Opcional: crear un nuevo refresh token
        
        # Devolver el nuevo access_token y refresh_token
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")