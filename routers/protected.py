from fastapi import Depends
from fastapi.routing import APIRouter
from dependencies.token import decode_token
from schemas.token import TokenSub

router = APIRouter()

@router.get('/protected')
def get_protected(user: TokenSub = Depends(decode_token)):
    return {"You are: ": user.username}