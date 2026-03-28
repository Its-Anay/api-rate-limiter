from .base import RateLimitStrategy
from redis.asyncio import Redis
import time

class LeakyBucketStrategy(RateLimitStrategy):
    LUA_SCRIPT = """
    local data = redis.call("HMGET", KEYS[1], "queue_size", "last_leak")
    local queue_size = tonumber(data[1])
    local last_leak = tonumber(data[2])

    if queue_size == nil then
        queue_size = 0
        last_leak = tonumber(ARGV[1])
    end

    local leaked = math.floor((tonumber(ARGV[1]) - last_leak) * tonumber(ARGV[3]))
    local new_queue_size = math.max(0, queue_size - leaked)

    if new_queue_size < tonumber(ARGV[2]) then
        redis.call("HMSET", KEYS[1], "queue_size", new_queue_size + 1, "last_leak", tonumber(ARGV[1]))
        return 1
    end

    return 0
    """
    
    REFILL_RATE = 1

    async def should_allow(self, redis: Redis, key: str, limit: int, window: int) -> bool:
        # 'key' is the rate_limit:user:ip:window string

        now = int(time.time())
        count = await redis.eval(self.LUA_SCRIPT, 1, key, now, limit,self.REFILL_RATE)
        return count == 1