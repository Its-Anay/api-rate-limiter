from abc import ABC, abstractmethod
from redis.asyncio import Redis

class RateLimitStrategy(ABC):
    @abstractmethod
    async def should_allow(self, redis: Redis, key: str, limit: int, window: int) -> bool:
        """
        Check if a request should be allowed based on the strategy.
        Returns True if allowed, False if blocked.
        """
        pass