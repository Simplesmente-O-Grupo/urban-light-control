from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from db.database import SessionLocal
from models.models import Reading 
from schemas.reading import ReadingCreate, ReadingRead
from typing import List, Optional

router = APIRouter(
    prefix='/readings',
    tags=['readings']
)

@router.get("/", response_model=List[ReadingRead])
def get_readings(
    sensor_id: Optional[int] = None,
    measure_type_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    db = SessionLocal()
    query = db.query(Reading)

    if sensor_id:
        query = query.filter(
            Reading.sensor_id == sensor_id
        )

    if measure_type_id:
        query = query.filter(
            Reading.measure_type_id == measure_type_id
        )

    readings = (
        query
        .order_by(Reading.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    db.close()

    return readings
