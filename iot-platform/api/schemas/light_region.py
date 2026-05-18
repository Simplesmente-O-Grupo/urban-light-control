from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LightRegionBase(BaseModel):
    name: str
    comments: Optional[str] = None
    installation_date: datetime
    address_id: int

class LightRegionCreate(LightRegionBase):
    pass


class LightRegionRead(LightRegionBase):
    id: int

    class Config:
        orm_mode = True
