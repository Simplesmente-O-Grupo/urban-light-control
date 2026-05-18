from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from db.database import SessionLocal
from models.models import MeasureType 
from schemas.measure_type import MeasureTypeCreate, MeasureTypeRead
from typing import List

router = APIRouter(
    prefix='/measure_types',
    tags=['measure_types']
)

@router.post("/", response_model=MeasureTypeRead)
def create_measure_type(
    measure_type: MeasureTypeCreate,
):
    db = SessionLocal()
    existing_measure_type = (
        db.query(MeasureType)
        .filter(MeasureType.name == measure_type.name)
        .first()
    )

    if existing_measure_type:
        raise HTTPException(
            status_code=400,
            detail="Measure type already exists"
        )

    db_measure_type = MeasureType(
        name=measure_type.name
    )

    db.add(db_measure_type)
    db.commit()
    db.refresh(db_measure_type)
    db.close()

    return db_measure_type

@router.get("/", response_model=List[MeasureTypeRead])
def get_measure_types(
    skip: int = 0,
    limit: int = 100,
):
    db = SessionLocal()
    measure_types = (
        db.query(MeasureType)
        .offset(skip)
        .limit(limit)
        .all()
    )

    db.close()
    return measure_types


@router.get("/{measure_type_id}", response_model=MeasureTypeRead)
def get_measure_type(
    measure_type_id: int,
):
    db = SessionLocal()
    measure_type = (
        db.query(MeasureType)
        .filter(MeasureType.id == measure_type_id)
        .first()
    )

    if not measure_type:
        raise HTTPException(
            status_code=404,
            detail="Measure type not found"
        )
    db.close()

    return measure_type
