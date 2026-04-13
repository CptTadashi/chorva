from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.user import AdminUser
from app.schemas.admin_mgmt import AdminUserRead, AdminUserCreate, AdminPasswordUpdate
from app.api.deps import get_superadmin, get_current_admin
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/staff", response_model=List[AdminUserRead])
async def get_all_admins(
    db: AsyncSession = Depends(get_db), 
    admin = Depends(get_superadmin)
):
    result = await db.execute(select(AdminUser).order_by(AdminUser.created_at.desc()))
    return result.scalars().all()

@router.post("/staff", response_model=AdminUserRead)
async def create_moderator(
    data: AdminUserCreate, 
    db: AsyncSession = Depends(get_db), 
    admin = Depends(get_superadmin)
):
    # Username mavjudligini tekshirish
    result = await db.execute(select(AdminUser).where(AdminUser.username == data.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username band")
        
    new_admin = AdminUser(
        username=data.username,
        password_hash=get_password_hash(data.password),
        role=data.role,
        is_active=True
    )
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin

@router.delete("/staff/{admin_id}")
async def delete_staff(
    admin_id: int, 
    db: AsyncSession = Depends(get_db), 
    admin = Depends(get_superadmin)
):
    target = await db.get(AdminUser, admin_id)
    if not target:
        raise HTTPException(status_code=404, detail="Admin topilmadi")
    
    if target.username == admin.username:
        raise HTTPException(status_code=400, detail="O'z profilini o'chirish mumkin emas")
        
    await db.delete(target)
    await db.commit()
    return {"message": "Admin o'chirildi"}

@router.patch("/staff/{admin_id}/password")
async def update_staff_password(
    admin_id: int,
    data: AdminPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    requester: AdminUser = Depends(get_current_admin)
):
    target = await db.get(AdminUser, admin_id)
    if not target:
        raise HTTPException(status_code=404, detail="Admin topilmadi")
    
    # Permission check: superadmin can change any, moderator only own
    if requester.role != "superadmin" and requester.id != admin_id:
        raise HTTPException(status_code=403, detail="Ruxsat berilmagan")
        
    target.password_hash = get_password_hash(data.new_password)
    await db.commit()
    return {"message": "Parol muvaffaqiyatli yangilandi"}
