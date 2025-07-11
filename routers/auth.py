from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.db import get_db
from services.user import UserService

from schemas.user import UserCredentialsEmail, UserSchema

router = APIRouter()

@router.post('/signup', response_model=UserSchema)
async def signup(
    user_credentials: UserCredentialsEmail,
    db: AsyncSession = Depends(get_db)
    ):
    return await UserService(db).signup(user_credentials)