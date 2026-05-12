from pydantic import BaseModel

class PostSensor(BaseModel):
    name: str
    light_region_id: int