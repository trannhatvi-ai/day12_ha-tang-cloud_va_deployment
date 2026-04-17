import time

import redis
from fastapi import HTTPException

from app.config import settings

r = redis.from_url(settings.redis_url, decode_responses=True)


def check_rate_limit(user_id: str) -> None:
    bucket = int(time.time() // 60)
    key = f"ratelimit:{user_id}:{bucket}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 120)

    if count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"},
        )
