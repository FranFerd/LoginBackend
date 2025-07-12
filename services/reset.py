from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.db import DbService

from configs.app_settings import settings

from schemas.email import EmailBody, EmailAddress

class ResetService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)

    async def reset_password(self, user_email: str):
        is_valid_email = await self.db_service.verify_email(email)

        if not is_valid_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email address"
            )

        email = EmailBody(
            from_=EmailAddress(email=settings.EMAIL_FROM, name="Your App"),
            to=[EmailAddress(email=user_email)],
            subject="Welcome!",
            html="<p>Thanks for joining us.</p>"
        )

        