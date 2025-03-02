from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.crud import user as user_crud

router = APIRouter()

@router.post('/{user_id}')
async def logout(user_id: UUID, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.is_active = False
    db.commit()
    return {"message": "Logout exitoso", "user_id": str(user.id), "is_active": user.is_active}