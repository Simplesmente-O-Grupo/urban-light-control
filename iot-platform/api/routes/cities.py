from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from db.database import SessionLocal
from models.models import City 
from schemas.city import CityRead, CityCreate
from typing import List

router = APIRouter(
    prefix='/cities',
    tags=['cities']
)

@router.get("/", response_model=List[CityRead])
def get_cities(
    skip: int = 0,
    limit: int = 100,
):
    session = SessionLocal()
    cities = session.query(City).offset(skip).limit(limit).all()
    session.close()
    return cities

@router.get("/{city_id}", response_model=CityRead)
def get_city(
    city_id: int,
):
    session = SessionLocal()
    city = session.query(City).filter(City.id == city_id).first()

    if not city:
        raise HTTPException(
            status_code=404,
            detail="City not found"
        )
    session.close()
    return city

@router.post("/", response_model=CityRead)
def create_city(
    city: CityCreate,
):
    session = SessionLocal()
    db_city = City(name=city.name)

    session.add(db_city)
    session.commit()
    session.refresh(db_city)
    session.close()

    return db_city
