from fastapi import FastAPI
from db.database import engine, Base

from models.models import City, Address, LightRegion, Sensor, Reading, MeasureType

Base.metadata.create_all(bind=engine)

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}