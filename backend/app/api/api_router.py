from fastapi import APIRouter
from app.api.endpoints import (
    public, bot_users, bot_ads, admin_ads, admin_auth, 
    admin_stats, admin_settings, admin_users, admin_staff
)

api_router = APIRouter()

api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(bot_users.router, prefix="/bot", tags=["bot_users"])
api_router.include_router(bot_ads.router, prefix="/bot/ads", tags=["bot_ads"])
api_router.include_router(admin_auth.router, prefix="/admin/auth", tags=["admin_auth"])
api_router.include_router(admin_ads.router, prefix="/admin/ads", tags=["admin_ads"])
api_router.include_router(admin_stats.router, prefix="/admin/stats", tags=["admin_stats"])
api_router.include_router(admin_settings.router, prefix="/admin/settings", tags=["admin_settings"])
api_router.include_router(admin_users.router, prefix="/admin/users", tags=["admin_users"])
api_router.include_router(admin_staff.router, prefix="/admin/staff", tags=["admin_staff"])
