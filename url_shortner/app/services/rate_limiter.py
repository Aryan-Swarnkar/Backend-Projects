from dataclasses import dataclass
from time import monotonic


@dataclass
class TokenBucket:
    capacity: float
    refill_rate: float
    tokens: float
    last_refill: float

    @classmethod
    def create(
        cls,
        capacity: float,
        refill_rate: float,
    ) -> "TokenBucket":
        now = monotonic()

        return cls(
            capacity=capacity,
            refill_rate=refill_rate,
            tokens=capacity,
            last_refill=now,
        )

    def refill(self) -> None:
        now = monotonic()

        elapsed = now - self.last_refill

        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate,
        )

        self.last_refill = now

    def consume(self, tokens: float = 1.0) -> bool:
        self.refill()

        if self.tokens < tokens:
            return False

        self.tokens -= tokens

        return True
    
    

import json 
import time

from redis.asyncio import Redis

RATE_LIMIT_CAPACITY = 10.0
RATE_LIMIT_REFILL_RATE = 1.0
RATE_LIMIT_KEY_TTL = 60

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
        
    def _build_key(self, identity: str) -> str:
        return f"rate_limit:user:{identity}"
    
    async def consume(
        self,
        identity: str,
        tokens: float = 1.0,
    ) -> bool:
        key = self._build_key(identity)
        
        current = await self.redis.get(key)
        
        now = time.time()
        
        if current is None:
            bucket = {
                "tokens": self.capacity,
                "last_refill": now,
            }
        else:
            bucket = json.loads(current)
            
        elapsed = now - bucket["last_refill"]
        
        bucket["tokens"] = min(
            self.capacity,
            bucket["tokens"] + elapsed * self.refill_rate,
        )

        bucket["last_refill"] = now
        
        if bucket["tokens"] < tokens:
            await self.redis.set(
                key,
                json.dumps(bucket),
                ex=RATE_LIMIT_KEY_TTL,
            )
            
            return False
        
        bucket["tokens"] -= tokens
        
        await self.redis.set(
            key,
            json.dumps(bucket),
            ex=RATE_LIMIT_KEY_TTL,
        )
        return True