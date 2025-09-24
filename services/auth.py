from logger.logger import logger

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from services.infrastructure.db import DbService
from services.infrastructure.token import token_service
from services.reset_confirm import ResetConfirmService
from services.infrastructure.redis import (
    redis_attempt_limiter,
    redis_user_for_signup,
    redis_email_code
)

from security.password_hashing import argon2_ph

from models.user import UserModel

from schemas.user import Credentials, UserSchema, CredentialsHashed, CodeAndEmail
from schemas.message import EmailConfirmMessage, UserRegisteredMessage
from schemas.token import TokenResponse
from schemas.exceptions import (
    DatabaseError, 
    UserAlreadyExistsError,   
    TokenCreationError
)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)
        self.helper = AuthServiceHelper(db)

    async def request_email_confirmation(self, credentials: Credentials) -> EmailConfirmMessage:
        logger.info(f"Signup attempt for user '{credentials.username}'")
        
        await self.helper.ensure_user_does_not_exist(credentials)
        
        credentials_hashed = self.helper.hash_credentials(credentials)

        await redis_user_for_signup.store_user_for_signup(credentials_hashed, 30)

        await ResetConfirmService(self.db_service).request_email_confirm(
            user_email=credentials.email,
            username=credentials.username
        )

        return EmailConfirmMessage(
            message=f"An email with confirmation code was sent to {credentials_hashed.email}"
        )
    
    async def register_user(self, code_and_email: CodeAndEmail) -> UserRegisteredMessage:
        logger.info(f"Email code verification attempt for user '{code_and_email.email}'")
        await self.helper.verify_email_confirmation_code(code_and_email)
        
        stored_credentials = await redis_user_for_signup.get_user_for_signup(code_and_email.email)
        new_user = await self.helper.insert_new_user(stored_credentials)

        await redis_email_code.delete_email_confirmation_code(code_and_email.email)

        logger.info(f"User with id {new_user.id} registered successfully")
        return UserRegisteredMessage(
            message=f"User {new_user.username} registered successfully"
        )

    async def token(self, credentials: OAuth2PasswordRequestForm) -> TokenResponse:
        try:
            logger.info(f"Login attempt for username: {credentials.username}")

            await self.helper.check_if_blocked(credentials)
            
            is_valid_user = await self.db_service.verify_user(credentials.username, credentials.password)
            if not is_valid_user:
                await self.helper.register_login_attempt(credentials)

            # If valid credentials
            return await self.helper.create_token(credentials)
        
        except (TokenCreationError, DatabaseError):
            logger.exception(f"Unexpected error during token generation")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation error"
            )

class AuthServiceHelper:
    def __init__(self, db: AsyncSession):
        self.db_service = DbService(db)
    
    async def ensure_user_does_not_exist(self, credentials: Credentials) -> None:
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
            logger.info(f"{credentials.username} doesn't exist")
            return

        else:
            raise DatabaseError("Unexpected number of users found")
        
    def hash_credentials(self, credentials: Credentials) -> CredentialsHashed:
        hashed_password = argon2_ph.hash_password(credentials.password)
        user_credentials_hashed = CredentialsHashed(
            username=credentials.username,
            hashed_password=hashed_password,
            email=credentials.email
        )
        return user_credentials_hashed
    
    async def verify_email_confirmation_code(self, code_and_email: CodeAndEmail) -> None:
        code_redis = await redis_email_code.get_email_confirmation_code(code_and_email.email)
        if code_redis is None:
            logger.info(f"Confirmation code for '{code_and_email.email} not found or expired'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Code expired or doesn't exist"
            )
        if code_and_email.code == code_redis:
            logger.info(f"Email code for '{code_and_email.email} confirmed successfully'")
            return
        
        logger.info(f"Incorrect email code attempt for '{code_and_email.email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Codes do not match"
        )
    
    async def insert_new_user(self, credentials_hashed: CredentialsHashed) -> UserSchema:
        try:
            new_user = await self.db_service.insert_user(credentials_hashed)
            logger.info(f"User {credentials_hashed.email} successfully registered")
            return UserSchema.model_validate(new_user)

        except UserAlreadyExistsError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already in use"
            )
        
        except DatabaseError:
            logger.exception(
                f"Unexpected error during signup for {credentials_hashed.username} / {credentials_hashed.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while signing up"
            )
        
    async def check_if_blocked(self, credentials: Credentials) -> None:
        is_blocked = await redis_attempt_limiter.is_blocked(credentials.username)
        if is_blocked:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts"
            )
        
    async def create_token(self, credentials: Credentials) -> TokenResponse:
        access_token = token_service.create_access_token(
            username=credentials.username,
            expires_minutes=15
        )

        logger.info(f"Access token issued for user {credentials.username}")
        await redis_attempt_limiter.reset_attempts(credentials.username)
        return TokenResponse(access_token=access_token, token_type='bearer')
        
    async def register_login_attempt(self, credentials: Credentials) -> None:
        await redis_attempt_limiter.register_attempt(credentials.username)
        logger.info(f"Failed login attempt for username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )