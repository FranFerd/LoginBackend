import asyncio

from typing import Callable

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.db import DbService
from services.email import email_service

class ResetConfirmService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)

    async def _request_email(self, user_email: str, func: Callable[[str], None]) -> None: # Callable [[arguments type], return type]
        try:
            is_valid_email = await self.db_service.verify_email(user_email)

            if not is_valid_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email address"
                )
            
            loop = asyncio.get_running_loop() # send_password is sync. executor runs blocking (synchronous) code in a separate thread without blocking async
            await loop.run_in_executor(None, func, user_email) 
        except HTTPException: # Without it, except Exception catches 'not is_valid_email' exception and overwrites it with 500.
            raise
        except Exception:
            raise
            
    async def request_password_reset(self, user_email: str) -> None:
        await self._request_email(user_email, email_service.send_password_reset_email)
    
    async def request_email_confirm(self, user_email: str) -> None:
        await self._request_email(user_email, email_service.send_email_confirm)