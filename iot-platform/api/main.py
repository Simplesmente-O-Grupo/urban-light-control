from fastapi import FastAPI

from db.database import engine, Base

from models.models import (
    City,
    Address,
    LightRegion,
    Sensor,
    Reading,
    MeasureType
)

from routes.sensors import router as sensor_router


app = FastAPI()


Base.metadata.create_all(bind=engine)


app.include_router(sensor_router)