import asyncio

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.db import DbService
from services.email import email_service

import logging
logger = logging.getLogger(__name__)

class ResetService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)

    async def request_password_reset(self, user_email: str) -> None:
        try:
            is_valid_email = await self.db_service.verify_email(user_email)

            if not is_valid_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email address"
                )
            
            loop = asyncio.get_running_loop() # send_password is sync. executor runs blocking (synchronous) code in a separate thread without blocking async
            await loop.run_in_executor(None, email_service.send_password_reset_email, user_email) 
        except HTTPException: # Without it, except Exception catches 'not is_valid_email' exception and overwrites it with 500.
            raise
        except Exception:
            logger.exception("Failed to send reset password email")
            raise 