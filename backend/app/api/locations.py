from fastapi import APIRouter, HTTPException
from app.database.schemas import LocationOut
from app.services.data_service import get_locations, get_location

router=APIRouter(prefix='/locations',tags=['locations'])
@router.get('',response_model=list[LocationOut])
def locations(): return get_locations()
@router.get('/{location_id}',response_model=LocationOut)
def location(location_id: str):
    item=get_location(location_id)
    if not item: raise HTTPException(404,'Location not found')
    return item
