from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ReadingBase(BaseModel):
    value: float
    intensity: float
    timestamp: datetime
    sensor_id: int
    measure_type_id: int

class ReadingCreate(ReadingBase):
    pass

class ReadingRead(ReadingBase):
    id: int

    class Config:
        orm_mode = True
