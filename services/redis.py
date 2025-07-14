from typing import Optional
from redis.asyncio import Redis
from configs.app_settings import settings

from datetime import timedelta


class RedisService:

    MAX_ATTEMPTS = 5
    EXPIRATION_TIME = 15 # seconds

    def __init__(self):
        self.client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )

    def _get_key_login_fail(self, username: str) -> str:
        return f"login_fail:{username}"
    
    def _get_key_password_reset_token(self, username: str) -> str:
        return f"token:{username}"
    
    async def register_attempt(self, username: str) -> None:
        key = self._get_key_login_fail(username)
        await self.client.incr(key) # incr also returns incremented value
        await self.client.expire(key, self.EXPIRATION_TIME)

    async def is_blocked(self, username: str) -> bool:
        key = self._get_key_login_fail(username)
        attempts: bytes = await self.client.get(key) # returns bytes or None -> converting is needed

        if attempts and int(attempts) >= self.MAX_ATTEMPTS:
            return True
        return False
    
    async def reset_attempts(self, username: str) -> None:
        key = self._get_key_login_fail(username)
        await self.client.delete(key)

    async def store_password_reset_token(self, username: str, token: str, minutes: int) -> None:
        key = self._get_key_password_reset_token(username)
        await self.client.setex(key, timedelta(minutes=minutes), token) # No need to json.dumps plain string

    async def get_password_reset_token(self, username: str) -> Optional[str]:
        key = self._get_key_password_reset_token(username)
        token: bytes = await self.client.get(key)
        return token.decode() if token else None # json.loads converts JSON str into dict. Not what I need.

    async def expire_token(self, username: str) -> None:
        key = self._get_key_password_reset_token(username)
        await self.client.delete(key)
        
redis_service = RedisService()