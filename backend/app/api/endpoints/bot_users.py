from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdateLocation, UserRead

router = APIRouter()

@router.post("/auth/register", response_model=UserRead)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.telegram_id == user_in.telegram_id))
    user = result.scalars().first()
    
    if user:
        # Update user details if necessary
        user.phone_number = user_in.phone_number
        if user_in.full_name:
            user.full_name = user_in.full_name
        if user_in.region_id:
            user.region_id = user_in.region_id
        if user_in.district_id:
            user.district_id = user_in.district_id
    else:
        # Create new user
        user = User(
            telegram_id=user_in.telegram_id,
            phone_number=user_in.phone_number,
            full_name=user_in.full_name,
            region_id=user_in.region_id,
            district_id=user_in.district_id
        )
        db.add(user)
    
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/users/{telegram_id}", response_model=UserRead)
async def get_user_by_telegram_id(telegram_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{telegram_id}/location", response_model=UserRead)
async def update_user_location(telegram_id: int, location_in: UserUpdateLocation, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.region_id = location_in.region_id
    user.district_id = location_in.district_id
    
    await db.commit()
    await db.refresh(user)
    return user
