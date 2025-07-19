import asyncio
from logger.logger import logger

from typing import Callable

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.token import decode_token

from services.infrastructure.db import DbService
from services.infrastructure.email import email_service
from services.infrastructure.token import token_service
from services.infrastructure.redis import redis_service

from schemas.user import PasswordResetRequest
from schemas.token import TokenResponse, TokenSub

class ResetConfirmService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db) # If db init fails, this will raise

    async def _request_email(
        self, 
        user_email: str, 
        func: Callable[[str], None], # Callable [[arguments type], return type]
        *args: str
    ) -> None: 
        
        is_valid_email = await self.db_service.verify_email(user_email)
        if not is_valid_email: # No logging here. verify_email already does it
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email address"
            )
        
        loop = asyncio.get_running_loop() # sending email is sync. executor runs blocking (synchronous) code in a separate thread without blocking async
        await loop.run_in_executor(None, func, user_email, *args) 
            
    async def request_password_reset(
        self, 
        user_email: str
    ) -> None:
        
        users = await self.db_service.get_user_by_username_or_email(email=user_email)
        user = users[0] # users is a list of one
        username = user.username
        token = token_service.create_access_token(username, expires_minutes=30)

        await redis_service.store_password_reset_token(username, token, expires_minutes=30)
        await self._request_email(user_email, email_service.send_password_reset_email, username, token)
    
    async def request_email_confirm(
        self, 
        user_email: str, 
        username: str
    ) -> None:
        
        await self._request_email(user_email, email_service.send_email_confirm, username)

    async def reset_password(
        self, 
        new_password_request: PasswordResetRequest, 
        password_reset_token: TokenResponse
    ) -> None:
        
        try:
            username: TokenSub = decode_token(password_reset_token.access_token)
            await token_service.validate_password_reset_token_from_redis(
                username.username, 
                password_reset_token.access_token
            )
            await self.db_service.update_password(username.username, new_password_request.new_password)
        except HTTPException as e:
            logger.warning(f"HTTPException during password reset: {e.detail}")
            raise
        except Exception as e:
            logger.exception("Unexpected error during password reset")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error during password reset"
            )
        return 'Password changed successfully'
