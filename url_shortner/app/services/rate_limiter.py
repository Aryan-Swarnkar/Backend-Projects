import json
import time
from app.core.config import settings

from redis.asyncio import Redis

from dataclasses import dataclass
import math


@dataclass
class RateLimitResult:
    allowed: bool
    remaining_tokens: float
    retry_after: int


TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]

local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])
local ttl = tonumber(ARGV[5])

local state = redis.call("GET", key)

local tokens
local last_refill

if state then
    local decoded = cjson.decode(state)

    tokens = tonumber(decoded["tokens"])
    last_refill = tonumber(decoded["last_refill"])
else
    tokens = capacity
    last_refill = now
end

local elapsed = now - last_refill

tokens = math.min(
    capacity,
    tokens + elapsed * refill_rate
)

last_refill = now

local allowed = 0

if tokens >= requested then
    tokens = tokens - requested
    allowed = 1
end

local new_state = cjson.encode({
    tokens = tokens,
    last_refill = last_refill
})

redis.call(
    "SET",
    key,
    new_state,
    "EX",
    ttl
)

local retry_after = 0

if allowed == 0 then
    retry_after = math.ceil(
        (requested - tokens) / refill_rate
    )
end

return {
    allowed,
    tostring(tokens),
    retry_after
}
"""


class RedisTokenBucket:
    def __init__(
        self,
        redis: Redis,
        capacity: float | None = None,
        refill_rate: float | None = None,
    ):
        self.redis = redis
        self.capacity = (
            capacity
            if capacity is not None
            else settings.RATE_LIMIT_CAPACITY
        )
        self.refill_rate = (
            refill_rate
            if refill_rate is not None
            else settings.RATE_LIMIT_REFILL_RATE
        )

        self.script = redis.register_script(
            TOKEN_BUCKET_SCRIPT
        )

    def _build_key(self, identity: str) -> str:
        return f"rate_limit:user:{identity}"

    async def consume(
        self,
        identity: str,
        tokens: float = 1.0,
    ) -> RateLimitResult:
        key = self._build_key(identity)

        result = await self.script(
            keys=[key],
            args=[
                self.capacity,
                self.refill_rate,
                time.time(),
                tokens,
                settings.RATE_LIMIT_KEY_TTL
            ],
        )
        allowed = int(result[0])
        remaining_tokens = float(result[1])
        retry_after = int(result[2])
        
        return RateLimitResult(
            allowed=allowed == 1,
            remaining_tokens=remaining_tokens,
            retry_after=retry_after,
        )
    
    
def get_rate_limiter(
    redis: Redis,
) -> RedisTokenBucket:
    return RedisTokenBucket(redis)