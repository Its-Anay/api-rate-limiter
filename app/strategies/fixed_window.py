from .base import RateLimitStrategy
from redis.asyncio import Redis

class FixedWindowStrategy(RateLimitStrategy):
    LUA_SCRIPT = """
    local current = redis.call("INCR", KEYS[1])
    if current == 1 then
        redis.call("EXPIRE", KEYS[1], ARGV[1])
    end
    return current
    """

    async def should_allow(self, redis: Redis, key: str, limit: int, window: int) -> bool:
        # 'key' is the rate_limit:user:ip:window string
        count = await redis.eval(self.LUA_SCRIPT, 1, key, window)
        return count <= limit