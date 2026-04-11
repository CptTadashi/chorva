from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user import AdminUser
from app.core.security import verify_password

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AdminUser).where(AdminUser.username == data.username))
    admin = result.scalars().first()
    
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol noto'g'ri"
        )
    
    # MVP uchun token sifatida username ni qaytaramiz (sodda usul)
    return {
        "access_token": f"token_{admin.username}",
        "token_type": "bearer",
        "username": admin.username,
        "role": admin.role
    }
