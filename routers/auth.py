from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.db import get_db
from services.auth import AuthService

from schemas.user import Credentials, UserSchema
from schemas.message import EmailConfirmMessage

router = APIRouter()

@router.post('/signup/request-confirmation', response_model=EmailConfirmMessage)
async def signup_request_confirm(
    user_credentials: Credentials,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService(db).signup(user_credentials)

@router.post('/signup/verify-email')
async def signup_verify_email():
    pass

@router.post('/token')
async def token(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    return await AuthService(db).token(user_credentials)