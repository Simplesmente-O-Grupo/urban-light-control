from pydantic import BaseModel

class MeasureTypeBase(BaseModel):
    name: str


class MeasureTypeCreate(MeasureTypeBase):
    pass


class MeasureTypeRead(MeasureTypeBase):
    id: int

    class Config:
        orm_mode = True
