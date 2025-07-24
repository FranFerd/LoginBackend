from logger.logger import logger

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from configs.app_settings import settings

from services.infrastructure.redis import redis_password_reset_token

from schemas.exceptions import InvalidTokenError, TokenNotFoundError, TokenCreationError

class TokenService:
    def create_access_token(self, username: str, expires_minutes: int) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        to_encode = {
            "sub": username,
            "exp": expires_at,
        }

        try:
            token = jwt.encode(to_encode, settings.JWT_SECRET, settings.ALGORITHM)
            return token
        
        except JWTError as e:
            logger.exception(f"Failed to create JWT token for user {username}")
            raise TokenCreationError from e     
    
    async def validate_password_reset_token_from_redis(self, username: str, token_to_validate: str):
        stored_token = await redis_password_reset_token.get_password_reset_token(username)
        if stored_token is None:
            logger.info(f"No password reset token found for user '{username}'")
            raise TokenNotFoundError("Token expired or doesn't exist")
        
        if token_to_validate != stored_token:
            logger.info(f"Password reset token for user '{username} doesn't match provided token'")
            raise InvalidTokenError("Invalid token")

token_service = TokenService()