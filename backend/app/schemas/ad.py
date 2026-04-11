from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

from .category import CategoryRead
from .location import RegionRead, DistrictRead
from .user import UserRead

class AdCreate(BaseModel):
    telegram_id: int
    category_id: int
    title: str
    description: str
    price: float
    extra_contact: Optional[str] = None
    region_id: int
    district_id: int

class AdMediaRead(BaseModel):
    id: int
    media_type: str
    file_path: str
    file_id_telegram: Optional[str] = None
    sort_order: int
    
    model_config = ConfigDict(from_attributes=True)

class AdRead(BaseModel):
    id: int
    user_id: int
    category_id: int
    region_id: int
    district_id: int
    title: str
    description: str
    price: float
    owner_phone: str
    extra_contact: Optional[str] = None
    status: str
    reject_reason: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    
    user: Optional[UserRead] = None
    category: CategoryRead
    region: RegionRead
    district: DistrictRead
    media_files: List[AdMediaRead] = []

    model_config = ConfigDict(from_attributes=True)
