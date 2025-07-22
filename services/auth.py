from logger.logger import logger

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from services.infrastructure.db import DbService
from services.infrastructure.token import token_service
from services.infrastructure.redis import redis_service
from services.reset_confirm import ResetConfirmService

from security.password_hashing import argon2_ph

from models.user import UserModel

from schemas.user import Credentials, UserSchema, CredentialsHashed
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

    async def _ensure_user_does_not_exist(self, credentials: Credentials) -> None:
        existing_users = await self.db_service.get_user_by_username_or_email(
                credentials.username, 
                credentials.email
            )
            
        if len(existing_users) == 2:
            logger.info(f"Signup rejected: username and email already in use for {credentials.email}")
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Username and email already in use"
                )
        
        elif len(existing_users) == 1:
            user: UserModel = existing_users[0] 
            if user.username == credentials.username:
                logger.info(f"Signup rejected: username already in use for '{credentials.username}'")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Username already exists")
            
            if user.email == credentials.email:
                logger.info(f"Signup rejected: email already in use for {credentials.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )
        
        elif len(existing_users) == 0:
            return

        else:
            raise DatabaseError("Unexpected number of users found")
        
    def _hash_credentials(self, credentials: Credentials) -> CredentialsHashed:
        hashed_password = argon2_ph.hash_password(credentials.password)
        user_credentials_hashed = CredentialsHashed(
            username=credentials.username,
            hashed_password=hashed_password,
            email=credentials.email
        )
        return user_credentials_hashed
    
    async def _verify_email_confirmation_code(self, code_to_verify: int, credentials: Credentials) -> bool:
        code_redis = await redis_service.get_email_confirmation_code(credentials.email)
        if code_redis is None:
            logger.info(f"Confirmation code for '{credentials.email} not found or expired'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code expired or doesn't exist"
            )
        if code_to_verify == code_redis:
            logger.info(f"Email code for '{credentials.email} confirmed successfully'")
            return True
        
        logger.info(f"Incorrect email code attempt for '{credentials.email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Codes do not match"
        )
            
    
    # async def _insert_user(self, credentials: Credentials):
    #     try:
    #         new_user = await self.db_service.insert_user(credentials)
    #         logger.info(f"User {credentials.email} successfully registered")
    #         return UserSchema.model_validate(new_user)

    #     except UserAlreadyExistsError:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Username or email already in use"
    #         )
        
    #     except DatabaseError:
    #         logger.exception(
    #             f"Unexpected error during signup for {credentials.username} / {credentials.email}"
    #         )
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="An unexpected error occurred while signing up"
    #         )

    async def signup(self, credentials: Credentials) -> None:
        
        await self._ensure_user_does_not_exist(credentials)
        
        credentials_hashed = self._hash_credentials(credentials)

        await redis_service.store_user_for_signup(credentials_hashed, 10)
        # await redis_service.get_user_for_signup(user_credentials_hashed.email)

        await ResetConfirmService(self.db_service).request_email_confirm(
            user_email=credentials.email,
            username=credentials.username
        )

        return EmailConfirmMessage(
            message=f"An email with confirmation code was sent to {credentials_hashed.email}"
        )

    async def token(self, credentials: OAuth2PasswordRequestForm) -> TokenResponse:
        try:
            logger.info(f"Login attempt for username: {credentials.username}")

            is_blocked = await redis_service.is_blocked(credentials.username)
            if is_blocked:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many attempts"
                )
            
            is_valid_user = await self.db_service.verify_user(credentials.username, credentials.password)
            if is_valid_user:
                access_token = token_service.create_access_token(
                    username=credentials.username,
                    expires_minutes=15
                )
                logger.info(f"Access token issued for user {credentials.username}")
                await redis_service.reset_attempts(credentials.username)
                return TokenResponse(access_token=access_token, token_type='bearer')

            # Invalid credentials
            await redis_service.register_attempt(credentials.username)
            logger.info(f"Failed login attempt for username: {credentials.username}")
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