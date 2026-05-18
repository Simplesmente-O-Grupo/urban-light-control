from pydantic import BaseModel

class CityBase(BaseModel):
    name: str


class CityCreate(CityBase):
    pass


class CityRead(CityBase):
    id: int

    class Config:
        orm_mode = True
