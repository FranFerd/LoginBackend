from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from services.db import DbService
from services.token import token_service
from services.redis import redis_service

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCredentialsEmail, UserSchema
from schemas.token import TokenResponse

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)

    async def signup(self, user_credentials_email: UserCredentialsEmail)-> UserSchema:
        # With Pydantic Models there's no need to validate if Models exist (e.g if user_credentials_email), Pydantic does it automatically

        existing_users = await self.db_service.get_user_by_username_or_email(
            user_credentials_email.username, 
            user_credentials_email.email)
        
        if not existing_users:
            new_user = await self.db_service.insert_user(user_credentials_email)
            return UserSchema.model_validate(new_user)

        if len(existing_users) == 2:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Username and email already in use"
                )
        
        user = existing_users[0] 
        if user.username == user_credentials_email.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Username already exists")
        if user.email == user_credentials_email.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while signing up"
        )

    async def token(self, user_credentials: OAuth2PasswordRequestForm)-> TokenResponse:
        is_blocked = await redis_service.is_blocked(user_credentials.username)
        if is_blocked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts"
            )
        
        is_valid_user = await self.db_service.verify_user(user_credentials.username, user_credentials.password)
        if is_valid_user:
            access_token = token_service.create_access_token(
                username=user_credentials.username,
                expires_minutes=15
            )
            await redis_service.reset_attempts(user_credentials.username)
            return TokenResponse(access_token=access_token, token_type='bearer')

        await redis_service.register_attempt(user_credentials.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )           