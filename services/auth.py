from logger.logger import logger

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from services.infrastructure.db import DbService
from services.infrastructure.token import token_service
from services.infrastructure.redis import redis_service

from security.password_hashing import argon2_ph

from models.user import UserModel

from schemas.user import UserCredentialsEmail, UserSchema, UserCredentialsEmailHashed
from schemas.message import EmailConfirmMessage
from schemas.token import TokenResponse
from schemas.exceptions import (
    DatabaseError, 
    UserAlreadyExistsError,   
    TokenCreationError
)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)

    async def _ensure_user_does_not_exist(self, user_credentials_email: UserCredentialsEmail) -> None:
        existing_users = await self.db_service.get_user_by_username_or_email(
                user_credentials_email.username, 
                user_credentials_email.email
            )
            
        if len(existing_users) == 2:
            logger.info(f"Signup rejected: username and email already in use for {user_credentials_email.email}")
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Username and email already in use"
                )
        
        elif len(existing_users) == 1:
            user: UserModel = existing_users[0] 
            if user.username == user_credentials_email.username:
                logger.info(f"Signup rejected: username already in use for '{user_credentials_email.username}'")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Username already exists")
            
            if user.email == user_credentials_email.email:
                logger.info(f"Signup rejected: email already in use for {user_credentials_email.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
        else:
            raise DatabaseError("Unexpected number of users found")
        
    def _hash_credentials(self, user_credentials_email: UserCredentialsEmail) -> UserCredentialsEmailHashed:
        hashed_password = argon2_ph.hash_password(user_credentials_email.password)
        user_credentials_hashed = UserCredentialsEmailHashed(
            username=user_credentials_email.username,
            hashed_password=hashed_password,
            email=user_credentials_email.email
        )
        return user_credentials_hashed

    async def signup(self, user_credentials_email: UserCredentialsEmail) -> None:
        try:
            self._ensure_user_does_not_exist(user_credentials_email)
            
            user_credentials_hashed = self._hash_credentials(user_credentials_email)

            await redis_service.store_user_for_signup(user_credentials_hashed, 30)
            await redis_service.get_user_for_signup(user_credentials_hashed.email)

            return EmailConfirmMessage(
                message=f"An email with confirmation code was sent to {user_credentials_hashed.email}"
            )
                

                # new_user = await self.db_service.insert_user(user_credentials_email)
                # logger.info(f"User {user_credentials_email.email} successfully registered")
                # return UserSchema.model_validate(new_user)
            

            
        except UserAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already in use"
            )
        
        except DatabaseError:
            logger.exception(
                f"Unexpected error during signup for {user_credentials_email.username} / {user_credentials_email.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while signing up"
            )

    async def token(self, user_credentials: OAuth2PasswordRequestForm) -> TokenResponse:
        try:
            logger.info(f"Login attempt for username: {user_credentials.username}")

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
                logger.info(f"Access token issued for user {user_credentials.username}")
                await redis_service.reset_attempts(user_credentials.username)
                return TokenResponse(access_token=access_token, token_type='bearer')

            # Invalid credentials
            await redis_service.register_attempt(user_credentials.username)
            logger.info(f"Failed login attempt for username: {user_credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        except (TokenCreationError, DatabaseError):
            logger.exception(f"Unexpected error during token generation")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation error"
            )