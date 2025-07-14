import asyncio

from typing import Callable

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.db import DbService
from services.email import email_service
from services.token import token_service
from services.redis import redis_service

class ResetConfirmService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)

    async def _request_email(self, user_email: str, func: Callable[[str], None], *args: str) -> None: # Callable [[arguments type], return type]
        try:
            is_valid_email = await self.db_service.verify_email(user_email)

            if not is_valid_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email address"
                )
            
            loop = asyncio.get_running_loop() # sending email is sync. executor runs blocking (synchronous) code in a separate thread without blocking async
            await loop.run_in_executor(None, func, user_email, *args) 
        except HTTPException: # Without it, except Exception catches 'not is_valid_email' exception and overwrites it with 500.
            raise             # This way it passes the HTTPException up
        except Exception as e:
            raise e
            
    async def request_password_reset(self, user_email: str) -> None:

        token = token_service.create_access_token(username, 15)
        redis_service.store_password_reset_token(username, token, 15)
        await self._request_email(user_email, email_service.send_password_reset_email, username, token)
    
    async def request_email_confirm(self, user_email: str, username: str) -> None:
        await self._request_email(user_email, email_service.send_email_confirm, username)

    async def reset_password(username: str, new_password: str, db: AsyncSession):
        await token_service.validate_token_from_redis(username, )