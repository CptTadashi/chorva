from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class DistrictBase(BaseModel):
    name: str

class DistrictCreate(DistrictBase):
    region_id: int
    sort_order: int = 0

class DistrictUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None

class DistrictRead(DistrictBase):
    id: int
    region_id: int
    sort_order: int
    
    model_config = ConfigDict(from_attributes=True)

class RegionBase(BaseModel):
    name: str

class RegionCreate(RegionBase):
    sort_order: int = 0

class RegionUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None

class RegionRead(RegionBase):
    id: int
    sort_order: int
    
    model_config = ConfigDict(from_attributes=True)

class RegionWithDistricts(RegionRead):
    districts: List[DistrictRead] = []
