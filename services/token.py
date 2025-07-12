from datetime import datetime, timedelta, timezone
from jose import jwt
from configs.app_settings import settings

class TokenService:
    def __init__(self):
        pass

    def create_access_token(self, username: str, expires_minutes: int) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        to_encode = {
            "sub": username,
            "exp": expires_at,
        }
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

token_service = TokenService()