from fastapi import APIRouter, HTTPException
from app.database.schemas import LoginIn, UserOut

router=APIRouter(prefix='/auth',tags=['auth'])

@router.post('/login',response_model=UserOut)
def login(payload: LoginIn):
    name=payload.name.strip(); email=payload.email.strip().lower()
    if not name: name='User'
    if '@' not in email: raise HTTPException(400,'A valid email address is required.')
    return {'name':name,'email':email,'authenticated':True}
