from fastapi import APIRouter
from app.api.api_v1.endpoints import login, user, logout, register, refresh, aeat_scrapper, aeat_scrapper_grid

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(refresh.router, prefix="/refresh", tags=["refresh"])
api_router.include_router(logout.router, prefix="/logout", tags=["logout"])
api_router.include_router(register.router, prefix="/auth", tags=["register"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(aeat_scrapper.router, prefix="/aeat_scrapper", tags=["aeat_scrapper"])
api_router.include_router(aeat_scrapper_grid.router, prefix="/aeat_scrapper_grid", tags=["aeat_scrapper_grid"])