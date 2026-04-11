from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class AdminUserBase(BaseModel):
    username: str
    role: str # superadmin | moderator

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUserRead(AdminUserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DashboardStats(BaseModel):
    total_ads: int
    pending_ads: int
    published_ads: int
    sold_ads: int
    total_users: int
    ads_by_category: List[dict] # [{name, count}]
    ads_by_region: List[dict]   # [{name, count}]

class AdminPasswordUpdate(BaseModel):
    new_password: str
