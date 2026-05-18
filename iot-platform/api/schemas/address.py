from pydantic import BaseModel

class AddressBase(BaseModel):
    street: str
    avenue: str
    zip_code: str
    city_id: int


class AddressCreate(AddressBase):
    pass

class AddressRead(AddressBase):
    id: int

    class Config:
        orm_mode = True
