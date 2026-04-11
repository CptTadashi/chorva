from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.ad import Ad
from app.models.moderation import ModerationLog
from app.schemas.ad import AdRead
from app.services.notification import notify_user
from app.services.telegram_post import post_ad_to_channel
from app.api.deps import get_current_admin, get_superadmin

router = APIRouter()

@router.get("/pending", response_model=List[AdRead])
async def get_pending_ads(db: AsyncSession = Depends(get_db), admin = Depends(get_current_admin)):
    """
    Moderatsiyani kutayotgan e'lonlar ro'yxati.
    """
    stmt = select(Ad).where(Ad.status == "pending_review").options(
        selectinload(Ad.user), selectinload(Ad.category),
        selectinload(Ad.region), selectinload(Ad.district),
        selectinload(Ad.media_files)
    ).order_by(Ad.created_at.asc())
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/all", response_model=List[AdRead])
async def get_all_ads(
    status: Optional[str] = None,
    q: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    """
    Barcha e'lonlar ro'yxati (filtrlash va sahifalash bilan).
    """
    stmt = select(Ad).options(
        selectinload(Ad.user), selectinload(Ad.category),
        selectinload(Ad.region), selectinload(Ad.district),
        selectinload(Ad.media_files)
    ).order_by(Ad.created_at.desc())
    
    if status:
        stmt = stmt.where(Ad.status == status)
    if q:
        stmt = stmt.where(Ad.title.ilike(f"%{q}%"))
        
    # Pagination
    stmt = stmt.offset((page - 1) * limit).limit(limit)
        
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{ad_id}", response_model=AdRead)
async def get_ad_detail(ad_id: int, db: AsyncSession = Depends(get_db), admin = Depends(get_current_admin)):
    """
    E'lonning to'liq ma'lumotini ko'rish.
    """
    stmt = select(Ad).where(Ad.id == ad_id).options(
        selectinload(Ad.user), selectinload(Ad.category),
        selectinload(Ad.region), selectinload(Ad.district),
        selectinload(Ad.media_files)
    )
    result = await db.execute(stmt)
    ad = result.scalars().first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

@router.post("/{ad_id}/approve", response_model=AdRead)
async def approve_ad(ad_id: int, db: AsyncSession = Depends(get_db), admin = Depends(get_current_admin)):
    """
    E'lonni tasdiqlash.
    """
    stmt = select(Ad).where(Ad.id == ad_id).options(selectinload(Ad.user))
    result = await db.execute(stmt)
    ad = result.scalars().first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    ad.status = "published"
    ad.published_at = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Log moderation
    log = ModerationLog(ad_id=ad.id, admin_user_id=admin.id, action="approve")
    db.add(log)
    
    await db.commit()
    await db.refresh(ad)
    
    # Barcha relationship'lar bilan qayta yuklash (Kanalga yuborish uchun)
    full_ad_stmt = select(Ad).where(Ad.id == ad_id).options(
        selectinload(Ad.user), selectinload(Ad.category),
        selectinload(Ad.region), selectinload(Ad.district),
        selectinload(Ad.media_files)
    )
    full_ad_res = await db.execute(full_ad_stmt)
    full_ad = full_ad_res.scalars().first()
    
    # Kanalga yuborish (Backgroundda qilish ham mumkin, lekin hozircha oddiy await)
    if full_ad:
        channel_msg_id = await post_ad_to_channel(full_ad)
        if channel_msg_id:
            full_ad.telegram_channel_message_id = channel_msg_id
            await db.commit()
            
        # Xabar yuborish
        await notify_user(full_ad.user.telegram_id, f"Tabriklaymiz! Sizning '{full_ad.title}' nomli e'loningiz tasdiqlandi va kanalga joylandi.")
    
    return full_ad

@router.post("/{ad_id}/reject", response_model=AdRead)
async def reject_ad(ad_id: int, reason: str = Body(..., embed=True), db: AsyncSession = Depends(get_db), admin = Depends(get_current_admin)):
    """
    E'lonni rad etish.
    """
    stmt = select(Ad).where(Ad.id == ad_id).options(selectinload(Ad.user))
    result = await db.execute(stmt)
    ad = result.scalars().first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    ad.status = "rejected"
    ad.reject_reason = reason
    
    # Log moderation
    log = ModerationLog(ad_id=ad.id, admin_user_id=admin.id, action="reject", reason=reason)
    db.add(log)
    
    await db.commit()
    await db.refresh(ad)
    
    # Xabar yuborish
    await notify_user(ad.user.telegram_id, f"Afsuski, sizning '{ad.title}' nomli e'loningiz rad etildi.\nSabab: {reason}")
    
    return await get_ad_detail(ad_id, db, admin)

@router.delete("/{ad_id}")
async def delete_ad(ad_id: int, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    """
    E'lonni o'chirish (Faqat superadmin).
    """
    ad = await db.get(Ad, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="E'lon topilmadi")
    
    await db.delete(ad)
    await db.commit()
    return {"message": "E'lon butunlay o'chirildi"}
