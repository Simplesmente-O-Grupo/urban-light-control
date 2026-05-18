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
from routes.addresses import router as address_router
from routes.cities import router as city_router
from routes.light_regions import router as light_regions_router
from routes.readings import router as readigns_router
from routes.measure_types import router as measure_types_router



app = FastAPI()


Base.metadata.create_all(bind=engine)


app.include_router(sensor_router)
app.include_router(address_router)
app.include_router(city_router)
app.include_router(light_regions_router)
app.include_router(readigns_router)
app.include_router(measure_types_router)
