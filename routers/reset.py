from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from services.reset import ResetService

from dependencies.db import get_db

from schemas.email import Email

router = APIRouter()

@router.post('/password-reset')
async def reset_password(
    email: Email,
    db: AsyncSession = Depends(get_db)
): 
    return await ResetService(db).reset_password(email.email)