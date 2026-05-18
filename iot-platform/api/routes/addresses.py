from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from db.database import SessionLocal
from models.models import Address, City
from schemas.address import AddressRead, AddressCreate
from typing import List

router = APIRouter(
    prefix='/addresses',
    tags=['addresses']
)

@router.get("/", response_model=List[AddressRead])
def get_addresses(
    skip: int = 0,
    limit: int = 100,
):
    session = SessionLocal()
    addresses = session.query(Address).offset(skip).limit(limit).all()
    session.close()
    return addresses

@router.get("/{address_id}", response_model=AddressRead)
def get_address(
    address_id: int,
):
    session = SessionLocal()
    address = session.query(Address).filter(Address.id == address_id).first()

    if not address:
        raise HTTPException(
            status_code=404,
            detail="City not found"
        )
    session.close()
    return address

@router.post("/", response_model=AddressRead)
def create_address(
    address: AddressCreate,
):
    db = SessionLocal()
    # Check if city exists
    city = db.query(City).filter(City.id == address.city_id).first()

    if not city:
        raise HTTPException(
            status_code=404,
            detail="City not found"
        )

    db_address = Address(
        street=address.street,
        avenue=address.avenue,
        zip_code=address.zip_code,
        city_id=address.city_id
    )

    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    db.close()

    return db_address
