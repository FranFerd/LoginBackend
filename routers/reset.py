from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from services.reset_confirm import ResetConfirmService

from dependencies.db import get_db
from dependencies.token import get_token_from_header

from schemas.user import Email, PasswordResetRequest, UsernameEmail
from schemas.token import TokenResponse

router = APIRouter()


@router.post('/email/request-confirmation')
async def send_confirm_email(
    username_email: UsernameEmail,
    db: AsyncSession = Depends(get_db)
):
    return await ResetConfirmService(db).request_email_confirm(
        user_email=username_email.email,
        username=username_email.username 
    )

@router.post('/password-reset-email')
async def send_reset_password_email(
    email: Email,
    db: AsyncSession = Depends(get_db)
): 
    return await ResetConfirmService(db).request_password_reset(
        email.address, 
    )

@router.post('/password-reset')
async def reset_password(
    new_password_request: PasswordResetRequest,
    password_reset_token: TokenResponse = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db)
):
    return await ResetConfirmService(db).reset_password(
        new_password_request, 
        password_reset_token
    )
