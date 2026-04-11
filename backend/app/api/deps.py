from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.user import AdminUser

async def get_current_admin(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    # Bearer prefiksini olib tashlash
    token = authorization
    if authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    
    if not token.startswith("token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri token formati"
        )
    
    username = token.replace("token_", "")
    result = await db.execute(select(AdminUser).where(AdminUser.username == username))
    admin = result.scalars().first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin topilmadi"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin faol emas"
        )
        
    return admin

async def get_superadmin(
    admin: AdminUser = Depends(get_current_admin)
) -> AdminUser:
    if admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faqat superadmin uchun ruxsat berilgan"
        )
    return admin
