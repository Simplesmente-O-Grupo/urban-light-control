from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# ---------------------------------
# City Class 
# ---------------------------------
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    addresses = relationship("Address", back_populates="city")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String, index=True)
    avenue = Column(String, index=True)
    zip_code = Column(String, index=True)

    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)

    city = relationship("City", back_populates="addresses")
    light_regions = relationship("LightRegion", back_populates="address")


class LightRegion(Base):
    __tablename__ = "light_regions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    installation_date = Column(DateTime, default=func.now())
    comments = Column(String)

    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False, index=True)

    address = relationship("Address", back_populates="light_regions")
    sensors = relationship("Sensor", back_populates="light_region")


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    active = Column(Boolean, default=True)

    light_region_id = Column(Integer, ForeignKey("light_regions.id"), nullable=False, index=True)

    light_region = relationship("LightRegion", back_populates="sensors")
    readings = relationship("Reading", back_populates="sensor")


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float)
    intensity = Column(Float)
    timestamp = Column(DateTime, default=func.now())

    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False, index=True)
    measure_type_id = Column(Integer, ForeignKey("measure_types.id"), nullable=False, index=True)

    sensor = relationship("Sensor", back_populates="readings")
    measure_type = relationship("MeasureType", back_populates="readings")


class MeasureType(Base):
    __tablename__ = "measure_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    readings = relationship("Reading", back_populates="measure_type")
