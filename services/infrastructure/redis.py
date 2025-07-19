from typing import Optional

from redis.asyncio import Redis
from configs.app_settings import settings
from logger.logger import logger

from datetime import timedelta


class RedisService:

    MAX_ATTEMPTS = 5
    EXPIRATION_TIME = 15 # seconds

    def __init__(self):
        try:
            self.client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
            logger.info(f"Redis initialized on port {settings.REDIS_PORT}")
        except Exception:
            logger.critical("Failed to initialize Redis client")
            raise # 'raise' is better that 'raise e' because traceback starts where the error happened, not where it was caught (raise e)

    def _get_key_login_fail(self, username: str) -> str:
        return f"login_fail:{username}"
    
    def _get_key_password_reset_token(self, username: str) -> str:
        return f"password_reset_token:{username}"
    
    async def register_attempt(self, username: str) -> None:
        key = self._get_key_login_fail(username)
        await self.client.incr(key) # incr also returns incremented value
        await self.client.expire(key, self.EXPIRATION_TIME)
        logger.info(f"Login attempt failed for user '{username}'")

    async def is_blocked(self, username: str) -> bool:
        key = self._get_key_login_fail(username)
        attempts: bytes = await self.client.get(key) # returns bytes or None -> converting is needed

        if attempts and int(attempts) >= self.MAX_ATTEMPTS:
            logger.info(f"Login limit exceeded: user '{username}' temporarily blocked")
            return True
        return False
    
    async def reset_attempts(self, username: str) -> None:
        key = self._get_key_login_fail(username)
        await self.client.delete(key)
        logger.info(f"Login attempts reset for user '{username}'")

    async def store_password_reset_token(self, username: str, token: str, expires_minutes: int) -> None:
        key = self._get_key_password_reset_token(username)
        await self.client.setex(key, timedelta(minutes=expires_minutes), token) # No need to json.dumps plain string
        logger.info(f"Password reset token stored for user '{username} for {expires_minutes} minutes'")

    async def get_password_reset_token(self, username: str) -> Optional[str]:
        key = self._get_key_password_reset_token(username)
        token: bytes = await self.client.get(key)
        return token.decode() if token else None # json.loads converts JSON str into dict. Not what I need.

    async def expire_password_reset_token(self, username: str) -> None:
        key = self._get_key_password_reset_token(username)
        await self.client.delete(key)
        logger.info(f"Password reset token expired for user '{username}'")

redis_service = RedisService()