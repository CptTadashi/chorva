from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.models.category import Category
from app.models.location import Region, District
from app.schemas.category import CategoryRead
from app.schemas.location import RegionRead, DistrictRead

router = APIRouter()

@router.get("/categories", response_model=List[CategoryRead])
async def read_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.is_active == True).order_by(Category.sort_order))
    return result.scalars().all()

@router.get("/regions", response_model=List[RegionRead])
async def read_regions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Region).order_by(Region.sort_order))
    return result.scalars().all()

@router.get("/regions/{region_id}/districts", response_model=List[DistrictRead])
async def read_districts(region_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(District).where(District.region_id == region_id).order_by(District.sort_order))
    return result.scalars().all()
from sqlalchemy.orm import selectinload
from app.models.ad import Ad
from app.schemas.ad import AdRead

@router.get("/ads", response_model=List[AdRead])
async def read_public_ads(
    category_id: int = None, 
    region_id: int = None, 
    page: int = 1, 
    limit: int = 20, 
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Ad).where(Ad.status == "published").options(
        selectinload(Ad.user), selectinload(Ad.category), 
        selectinload(Ad.region), selectinload(Ad.district), selectinload(Ad.media_files)
    )
    if category_id:
        stmt = stmt.where(Ad.category_id == category_id)
    if region_id:
        stmt = stmt.where(Ad.region_id == region_id)
        
    # Ko'proq moslashuvchanlik uchun: published_at bo'sh bo'lsa created_at bo'yicha saralaymiz
    stmt = stmt.order_by(func.coalesce(Ad.published_at, Ad.created_at).desc())
    
    stmt = stmt.offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/ads/{ad_id}", response_model=AdRead)
async def read_public_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Ad).where(Ad.id == ad_id, Ad.status == "published").options(
        selectinload(Ad.user), selectinload(Ad.category), 
        selectinload(Ad.region), selectinload(Ad.district), selectinload(Ad.media_files)
    )
    result = await db.execute(stmt)
    ad = result.scalars().first()
    if not ad:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="E'lon topilmadi")
    return ad
