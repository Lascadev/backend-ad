from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.api.deps import get_db
from app.core.security import create_access_token, create_refresh_token, verify_password, decode_refresh_token, validate_refresh_token
from app.crud.user import get_user_by_email
from app.schemas.token import Token
from app.schemas.user import UserOut
from app.core.config import settings
from jose import JWTError, ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login/token")


@router.post("/token", response_model=Token)
def login_for_access_token(
        db: Session = Depends(get_db), 
        form_data: OAuth2PasswordRequestForm = Depends()
    ):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o Contraseña Incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        user.is_active = True
        db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.email})
    user_response = UserOut.model_validate(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user_response
    }
