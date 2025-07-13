from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from services.reset_confirm import ResetConfirmService

from dependencies.db import get_db

from pydantic import BaseModel, EmailStr

router = APIRouter()
class Email(BaseModel):
    email: EmailStr

@router.post('/password-reset')
async def send_reset_password_email(
    email: Email,
    db: AsyncSession = Depends(get_db)
): 
    return await ResetConfirmService(db).request_password_reset(email.email)

@router.post('/email-confirm')
async def send_confirm_email(
    email: Email,
    db: AsyncSession = Depends(get_db)
):
    return await ResetConfirmService(db).request_email_confirm(email.email)