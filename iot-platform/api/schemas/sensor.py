from pydantic import BaseModel

class SensorBase(BaseModel):
    name: str
    active: bool = True
    light_region_id: int


class SensorCreate(SensorBase):
    pass

class SensorRead(SensorBase):
    id: int

    class Config:
        orm_mode = True
