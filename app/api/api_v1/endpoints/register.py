from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.api.deps import get_db
from app.crud.user import get_user_by_email, create_user
from app.schemas.token import Token
from app.core.config import settings
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register_and_login(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db=db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Correo ya existe")

    try:
        db_user = create_user(db=db, user=user)
        if db_user:
            user_response = UserOut.from_orm(db_user)
            return user_response
    except IntegrityError as e:
        error_message = str(e.orig)
        if "email" in error_message:
            detail = "El correo electrónico ingresado ya está registrado."
        else:
            detail = "Error al crear el usuario. Inténtalo de nuevo."
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error inesperado al crear el usuario")
