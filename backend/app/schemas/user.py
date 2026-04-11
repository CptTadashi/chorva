from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    telegram_id: int
    phone_number: str

class UserCreate(UserBase):
    full_name: Optional[str] = None
    region_id: Optional[int] = None
    district_id: Optional[int] = None

class UserUpdateLocation(BaseModel):
    region_id: int
    district_id: int

class UserRead(UserBase):
    id: int
    full_name: Optional[str] = None
    region_id: Optional[int] = None
    district_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
