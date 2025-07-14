from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from services.reset_confirm import ResetConfirmService

from dependencies.db import get_db

from pydantic import BaseModel, EmailStr, Field

router = APIRouter()
class UsernameEmail(BaseModel):
    email: EmailStr = Field(max_length=254)
    username: str = Field(max_length=12)

@router.post('/password-reset')
async def send_reset_password_email(
    username_and_email: UsernameEmail,
    db: AsyncSession = Depends(get_db)
): 
    return await ResetConfirmService(db).request_password_reset(
        username_and_email.email, 
        username_and_email.username
    )

@router.post('/email-confirm')
async def send_confirm_email(
    username_and_email: UsernameEmail,
    db: AsyncSession = Depends(get_db)
):
    return await ResetConfirmService(db).request_email_confirm(
        username_and_email.email, 
        username_and_email.username
    )