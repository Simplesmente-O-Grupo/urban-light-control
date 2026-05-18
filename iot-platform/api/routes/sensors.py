from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from db.database import SessionLocal
from models.models import Sensor, LightRegion
from schemas.sensor import SensorCreate, SensorRead
from typing import List

router = APIRouter(
    prefix='/sensors',
    tags=['sensors']
)

@router.post("/", response_model=SensorRead)
def create_sensor(
    sensor: SensorCreate,
):
    db = SessionLocal()
    # Check if light region exists
    light_region = (
        db.query(LightRegion)
        .filter(LightRegion.id == sensor.light_region_id)
        .first()
    )

    if not light_region:
        raise HTTPException(
            status_code=404,
            detail="Light region not found"
        )

    db_sensor = Sensor(
        name=sensor.name,
        active=sensor.active,
        light_region_id=sensor.light_region_id
    )

    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    db.close()

    return db_sensor

@router.get("/", response_model=List[SensorRead])
def get_sensors(
    skip: int = 0,
    limit: int = 100,
):
    db = SessionLocal()

    sensors = (
        db.query(Sensor)
        .offset(skip)
        .limit(limit)
        .all()
    )
    db.close()

    return sensors

@router.get("/{sensor_id}", response_model=SensorRead)
def get_sensor(
    sensor_id: int,
):
    db = SessionLocal()
    sensor = (
        db.query(Sensor)
        .filter(Sensor.id == sensor_id)
        .first()
    )

    if not sensor:
        raise HTTPException(
            status_code=404,
            detail="Sensor not found"
        )

    db.close()

    return sensor
