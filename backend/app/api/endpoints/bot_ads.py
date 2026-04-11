import os
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.models.ad import Ad, AdMedia
from app.models.user import User
from app.schemas.ad import AdCreate, AdRead, AdMediaRead

router = APIRouter()
MEDIA_DIR = "media/"

@router.post("/", response_model=AdRead)
async def create_ad(ad_in: AdCreate, db: AsyncSession = Depends(get_db)):
    # Validate user
    user_result = await db.execute(select(User).where(User.telegram_id == ad_in.telegram_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_ad = Ad(
        user_id=user.id,
        category_id=ad_in.category_id,
        region_id=ad_in.region_id,
        district_id=ad_in.district_id,
        title=ad_in.title,
        description=ad_in.description,
        price=ad_in.price,
        owner_phone=user.phone_number,
        extra_contact=ad_in.extra_contact,
        status="pending_review"
    )
    db.add(new_ad)
    await db.commit()
    await db.refresh(new_ad)

    # Re-fetch with relationships
    stmt = select(Ad).where(Ad.id == new_ad.id).options(
        selectinload(Ad.user),
        selectinload(Ad.category),
        selectinload(Ad.region),
        selectinload(Ad.district),
        selectinload(Ad.media_files)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


@router.post("/{ad_id}/media", response_model=AdMediaRead)
async def upload_ad_media(
    ad_id: int, 
    file: UploadFile = File(...), 
    media_type: str = Form("photo"), 
    sort_order: int = Form(0), 
    db: AsyncSession = Depends(get_db)
):
    # Check ad exists
    ad_result = await db.execute(select(Ad).where(Ad.id == ad_id))
    ad = ad_result.scalars().first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
        
    # Xavfsizlik: Fayl hajmini tekshirish (20 MB)
    MAX_FILE_SIZE = 20 * 1024 * 1024
    # FastAPI/Starlette UploadFile.size dan foydalanamiz
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Fayl hajmi juda katta (maksimal 20 MB)")

    os.makedirs(MEDIA_DIR, exist_ok=True)
    extension = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid4()}.{extension}"
    file_path = os.path.join(MEDIA_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    ad_media = AdMedia(
        ad_id=ad_id,
        media_type=media_type,
        file_path=file_path,
        sort_order=sort_order
    )
    db.add(ad_media)
    await db.commit()
    await db.refresh(ad_media)
    return ad_media

@router.post("/{ad_id}/submit", response_model=AdRead)
async def submit_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    # Check ad exists
    stmt = select(Ad).where(Ad.id == ad_id).options(
        selectinload(Ad.user), selectinload(Ad.category), 
        selectinload(Ad.region), selectinload(Ad.district), selectinload(Ad.media_files)
    )
    ad_result = await db.execute(stmt)
    ad = ad_result.scalars().first()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
        
    if not ad.media_files:
        raise HTTPException(status_code=400, detail="Ad has no media attached")
        
    ad.status = "pending_review" # Resets it to pending review explicitly 
    await db.commit()
    await db.refresh(ad)
    return ad

@router.get("/users/{telegram_id}", response_model=List[AdRead])
async def get_user_ads(
    telegram_id: int, 
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    stmt = select(Ad).where(
        Ad.user_id == user.id,
        Ad.status.in_(["pending_review", "published"])
    ).options(
        selectinload(Ad.user), selectinload(Ad.category), 
        selectinload(Ad.region), selectinload(Ad.district), selectinload(Ad.media_files)
    ).order_by(Ad.created_at.desc())
    
    # Pagination
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    
    ads = await db.execute(stmt)
    return ads.scalars().all()


@router.post("/{ad_id}/sold", response_model=AdRead)
async def mark_ad_as_sold(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ad).where(Ad.id == ad_id))
    ad = result.scalars().first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    ad.status = "sold"
    await db.commit()

    # Barcha boglanishlar bilan qayta yuklash
    stmt = select(Ad).where(Ad.id == ad_id).options(
        selectinload(Ad.user), selectinload(Ad.category),
        selectinload(Ad.region), selectinload(Ad.district),
        selectinload(Ad.media_files)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


@router.post("/{ad_id}/cancel", response_model=AdRead)
async def cancel_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ad).where(Ad.id == ad_id))
    ad = result.scalars().first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    ad.status = "archive"
    await db.commit()

    # Barcha boglanishlar bilan qayta yuklash
    stmt = select(Ad).where(Ad.id == ad_id).options(
        selectinload(Ad.user), selectinload(Ad.category),
        selectinload(Ad.region), selectinload(Ad.district),
        selectinload(Ad.media_files)
    )
    result = await db.execute(stmt)
    return result.scalars().first()
