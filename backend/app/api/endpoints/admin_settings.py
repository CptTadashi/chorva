from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.category import Category
from app.models.location import Region, District
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.schemas.location import RegionCreate, RegionUpdate, RegionRead, DistrictCreate, DistrictUpdate, DistrictRead
from app.api.deps import get_superadmin

router = APIRouter()

# --- Categories ---
@router.post("/categories", response_model=CategoryRead)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@router.patch("/categories/{cat_id}", response_model=CategoryRead)
async def update_category(cat_id: int, data: CategoryUpdate, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    category = await db.get(Category, cat_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    
    await db.commit()
    await db.refresh(category)
    return category

# --- Regions ---
@router.post("/regions", response_model=RegionRead)
async def create_region(data: RegionCreate, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    region = Region(**data.model_dump())
    db.add(region)
    await db.commit()
    await db.refresh(region)
    return region

@router.patch("/regions/{reg_id}", response_model=RegionRead)
async def update_region(reg_id: int, data: RegionUpdate, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    region = await db.get(Region, reg_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(region, key, value)
    
    await db.commit()
    await db.refresh(region)
    return region

# --- Districts ---
@router.post("/districts", response_model=DistrictRead)
async def create_district(data: DistrictCreate, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    district = District(**data.model_dump())
    db.add(district)
    await db.commit()
    await db.refresh(district)
    return district

@router.patch("/districts/{dist_id}", response_model=DistrictRead)
async def update_district(dist_id: int, data: DistrictUpdate, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    district = await db.get(District, dist_id)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(district, key, value)
    
    await db.commit()
    await db.refresh(district)
    return district

# --- DELETE Operations ---

@router.delete("/categories/{cat_id}")
async def delete_category(cat_id: int, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    category = await db.get(Category, cat_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
    return {"detail": "Category deleted"}

@router.delete("/regions/{reg_id}")
async def delete_region(reg_id: int, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    region = await db.get(Region, reg_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    await db.delete(region)
    await db.commit()
    return {"detail": "Region deleted"}

@router.delete("/districts/{dist_id}")
async def delete_district(dist_id: int, db: AsyncSession = Depends(get_db), admin = Depends(get_superadmin)):
    district = await db.get(District, dist_id)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    await db.delete(district)
    await db.commit()
    return {"detail": "District deleted"}
