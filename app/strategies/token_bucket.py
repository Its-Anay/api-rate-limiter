from .base import RateLimitStrategy
from redis.asyncio import Redis
import time

class TokenBucketStrategy(RateLimitStrategy):
    LUA_SCRIPT = """
        local data = redis.call("HMGET", KEYS[1], "tokens", "last_refill")
        local tokens = tonumber(data[1])
        local last_refill = tonumber(data[2])

        if tokens == nil then
            tokens = tonumber(ARGV[2])
            last_refill = tonumber(ARGV[1])
        end

        local tokens_to_add = (tonumber(ARGV[1]) - last_refill) * tonumber(ARGV[3])
        local new_tokens = math.min(tokens + tokens_to_add, tonumber(ARGV[2]))

        if new_tokens >= 1 then
            local current_token = new_tokens - 1
            redis.call("HMSET", KEYS[1], "tokens", current_token, "last_refill", tonumber(ARGV[1]))
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