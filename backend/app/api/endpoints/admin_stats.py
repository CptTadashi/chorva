from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.core.database import get_db
from app.models.ad import Ad
from app.models.user import User
from app.models.category import Category
from app.models.location import Region
from app.schemas.admin_mgmt import DashboardStats
from app.api.deps import get_current_admin

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_current_admin)
):
    # Jami e'lonlar
    total_ads = await db.scalar(select(func.count(Ad.id)))
    pending_ads = await db.scalar(select(func.count(Ad.id)).where(Ad.status == "pending_review"))
    published_ads = await db.scalar(select(func.count(Ad.id)).where(Ad.status == "published"))
    sold_ads = await db.scalar(select(func.count(Ad.id)).where(Ad.status == "sold"))
    
    # Jami userlar
    total_users = await db.scalar(select(func.count(User.id)))
    
    # Kategoriya bo'yicha statistika
    cat_query = await db.execute(
        select(Category.name, func.count(Ad.id))
        .join(Ad, Ad.category_id == Category.id)
        .group_by(Category.name)
    )
    ads_by_category = [{"name": row[0], "count": row[1]} for row in cat_query.all()]
    
    # Hudud bo'yicha statistika
    reg_query = await db.execute(
        select(Region.name, func.count(Ad.id))
        .join(Ad, Ad.region_id == Region.id)
        .group_by(Region.name)
    )
    ads_by_region = [{"name": row[0], "count": row[1]} for row in reg_query.all()]
    
    return {
        "total_ads": total_ads or 0,
        "pending_ads": pending_ads or 0,
        "published_ads": published_ads or 0,
        "sold_ads": sold_ads or 0,
        "total_users": total_users or 0,
        "ads_by_category": ads_by_category,
        "ads_by_region": ads_by_region
    }
