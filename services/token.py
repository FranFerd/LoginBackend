from fastapi import HTTPException, status
from jose import jwt
from datetime import datetime, timedelta, timezone

from configs.app_settings import settings

from services.redis import redis_service

from schemas.token import TokenSub

class TokenService:
    def create_access_token(self, username: str, expires_minutes: int) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        to_encode = {
            "sub": username,
            "exp": expires_at,
        }
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    
    async def validate_token_from_redis(username: TokenSub, token: str):
        stored_token = await redis_service.get_password_reset_token(username.username)

        if stored_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired or not found"
            )
        
        if token != stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

token_service = TokenService()