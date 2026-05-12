from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Sensor, LightRegion
from ..schemas.sensor import PostSensor

router = APIRouter(
    prefix='/sensors',
    tags=['sensors']
)

@router.get('/')
async def get_sensors():
    dc = {'sensors': []}
    session = SessionLocal()
    try:
        stmt = select(Sensor)
        devices = session.execute(stmt)
        for device in devices.scalars():
            dev = {
                'id': device.id,
                'name': device.name,
                'light_region_id': device.light_region_id,
                'active': device.active
                }
            dc['sensors'].append(dev)
        dc['size'] = len(dc['sensors'])
        session.close()
        return dc
    finally:        
        session.close()

@router.post('/')
async def post_sensor(sensor: PostSensor):
    session = SessionLocal()
    light_region = session.get(LightRegion, sensor.light_region_id)
    if not light_region:
        session.close()
        raise HTTPException(
            status_code=404,
            detail=f"Não existe região de iluminação com id {sensor.light_region_id}"
        )

    session.add(Sensor(name=sensor.name, light_region_id=sensor.light_region_id, is_active=True))
    session.commit()
    session.close()
    return {'msg': 'Sensor criado com sucesso.'}
