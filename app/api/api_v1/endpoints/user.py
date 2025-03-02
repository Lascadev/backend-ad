from fastapi import APIRouter,Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_active_user
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserOut, UserUpdate, PasswordUpdate
from app.models.user import User
from uuid import UUID
from sqlalchemy.exc import IntegrityError

router = APIRouter()

#crear usuario
@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db=db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Correo ya existe")
    try:
        db_user = user_crud.create_user(db=db, user=user)
        if db_user:
            return db_user
    except IntegrityError as e:
        error_message = str(e.orig)
        if "email" in error_message:
            detail = "El correo electrónico ingresado ya está registrado."
        else:
            detail = "Error al crear el usuario. Inténtalo de nuevo."

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error inesperado al crear el usuario")

#actualizar usuario
@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id:UUID, user_in: UserUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    print(f"Datos recibidos para actualización: {user_in.dict()}")
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    db_user = user_crud.update_user(db=db, user_id=user_id, user_in=user_in)
    if db_user:
        return db_user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

#actualizar password
@router.put("/{user_id}/password", response_model=dict)
def change_password(
    user_id: UUID,
    password_data: PasswordUpdate,  # Usamos el esquema PasswordUpdate
    db: Session = Depends(get_db)
):
    try:
        user = user_crud.update_user_password(db, user_id, password_data.current_password, password_data.new_password)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        return {"message": "Contraseña actualizada con éxito."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

#eliminar usuario
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este usuario"
        )
    
    user_crud.delete_user(db=db, user_id=user_id)
    return {"message": "Usuario Eliminado Satisfactoriamente"}

#obtener usuario por id
@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id:UUID, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este usuario")
    user = user_crud.get_user_by_id(db=db, user_id=user_id)

    if user:
        return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

#obtener usuario por email
@router.get("/email/{email}", response_model=UserOut)
def get_user_by_email(
    email: str, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta información")
    
    user = user_crud.get_user_by_email(db=db, email=email)
    if user:
        return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

#obtener usuario por telefono
@router.get("/phone/{phone}", response_model=UserOut)
def get_user_by_phone(
    phone: str, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta información")
    user = user_crud.get_user_by_phone(db=db, phone=phone)
    if user:
        return user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

#obtener usuario por nombre y apellido
@router.get("/name/{name}", response_model=List[UserOut])
def get_user_by_name(
    name: str, db:Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta información")
    users = user_crud.get_user_by_name(db=db, name=name)
    return users

#obtener usuarios
@router.get('/', response_model=List[UserOut])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 10,
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta información")
    users = user_crud.get_users(db=db, skip=skip, limit=limit)
    return users
