from redis.asyncio import Redis
from configs.app_settings import settings


class RedisService:

    MAX_ATTEMPTS = 5
    EXPIRATION_TIME = 15
    PREFIX = "login_fail"

    def __init__(self):
        self.client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )

    def _get_key(self, username: str) -> str:
        return f"{self.PREFIX}:{username}"
    
    async def register_attempt(self, username: str) -> None:
        key = self._get_key(username)
        await self.client.incr(key) # incr also returns incremented value
        await self.client.expire(key, self.EXPIRATION_TIME)

    async def is_blocked(self, username: str) -> bool:
        key = self._get_key(username)
        attempts: bytes = await self.client.get(key) # returns bytes or None -> converting is needed

        if attempts and int(attempts) >= self.MAX_ATTEMPTS:
            return True
        return False
    
    async def reset_attempts(self, username: str) -> None:
        key = self._get_key(username)
        await self.client.delete(key)

redis_service = RedisService()