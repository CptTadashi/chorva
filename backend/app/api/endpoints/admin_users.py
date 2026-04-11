from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.api.deps import get_superadmin

router = APIRouter()

@router.get("/users", response_model=List[UserRead])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    admin = Depends(get_superadmin)
):
    result = await db.execute(select(User).offset(skip).limit(limit).order_by(User.created_at.desc()))
    return result.scalars().all()

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    admin = Depends(get_superadmin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = not user.is_active
    await db.commit()
    return {"message": f"User status changed to {'active' if user.is_active else 'inactive'}", "is_active": user.is_active}
