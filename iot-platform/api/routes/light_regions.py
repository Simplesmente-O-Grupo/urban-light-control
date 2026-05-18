from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from db.database import SessionLocal
from models.models import LightRegion, Address
from schemas.light_region import LightRegionCreate, LightRegionRead
from typing import List

router = APIRouter(
    prefix='/light_regions',
    tags=['light_regions']
)

@router.post("/", response_model=LightRegionRead)
def create_light_region(
    light_region: LightRegionCreate,
):
    db = SessionLocal()
    # Check if address exists
    address = (
        db.query(Address)
        .filter(Address.id == light_region.address_id)
        .first()
    )

    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    db_light_region = LightRegion(
        name=light_region.name,
        comments=light_region.comments,
        address_id=light_region.address_id
    )

    db.add(db_light_region)
    db.commit()
    db.refresh(db_light_region)
    db.close()

    return db_light_region

@router.get("/", response_model=List[LightRegionRead])
def get_light_regions(
    skip: int = 0,
    limit: int = 100,
):
    db = SessionLocal()
    light_regions = (
        db.query(LightRegion)
        .offset(skip)
        .limit(limit)
        .all()
    )

    db.close()

    return light_regions

@router.get("/{light_region_id}", response_model=LightRegionRead)
def get_light_region(
    light_region_id: int,
):
    db = SessionLocal()
    light_region = (
        db.query(LightRegion)
        .filter(LightRegion.id == light_region_id)
        .first()
    )

    if not light_region:
        raise HTTPException(
            status_code=404,
            detail="Light region not found"
        )

    db.close()
    return light_region
