from .base import RateLimitStrategy
from redis.asyncio import Redis
import uuid
import time

class SlidingWindowStrategy(RateLimitStrategy):
    LUA_SCRIPT = """
    redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, ARGV[1] - ARGV[2])
    local count = redis.call("ZCARD", KEYS[1])
    redis.call("ZADD", KEYS[1], ARGV[1], ARGV[3])
    redis.call("EXPIRE", KEYS[1], ARGV[2])
    return count
    """

    async def should_allow(self, redis: Redis, key: str, limit: int, window: int) -> bool:
        # 'key' is the rate_limit:user:ip:window string
        now = int(time.time())
        unique_id = str(uuid.uuid4())
        count = await redis.eval(self.LUA_SCRIPT, 1, key, now, window, unique_id)
        return count < limit