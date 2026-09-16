import json
import time

from redis.asyncio import Redis


RATE_LIMIT_CAPACITY = 10.0
RATE_LIMIT_REFILL_RATE = 1.0
RATE_LIMIT_KEY_TTL = 60


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

return {
    allowed,
    tostring(tokens)
}
"""


class RedisTokenBucket:
    def __init__(
        self,
        redis: Redis,
        capacity: float = RATE_LIMIT_CAPACITY,
        refill_rate: float = RATE_LIMIT_REFILL_RATE,
    ):
        self.redis = redis
        self.capacity = capacity
        self.refill_rate = refill_rate

        self.script = redis.register_script(
            TOKEN_BUCKET_SCRIPT
        )

    def _build_key(self, identity: str) -> str:
        return f"rate_limit:user:{identity}"

    async def consume(
        self,
        identity: str,
        tokens: float = 1.0,
    ) -> bool:
        key = self._build_key(identity)

        result = await self.script(
            keys=[key],
            args=[
                self.capacity,
                self.refill_rate,
                time.time(),
                tokens,
                RATE_LIMIT_KEY_TTL,
            ],
        )

        allowed = int(result[0])

        return allowed == 1
    
    
def get_rate_limiter(
    redis: Redis,
) -> RedisTokenBucket:
    return RedisTokenBucket(redis)