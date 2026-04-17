from datetime import datetime, timezone

import redis
from fastapi import HTTPException

from app.config import settings

r = redis.from_url(settings.redis_url, decode_responses=True)


def _month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def check_budget(user_id: str) -> None:
    key = f"budget:{user_id}:{_month_key()}"
    current = float(r.get(key) or 0.0)
    projected = current + settings.estimated_cost_per_request_usd
    if projected > settings.monthly_budget_usd:
        raise HTTPException(status_code=402, detail="Monthly budget exceeded")


def record_usage(user_id: str, request_cost: float) -> float:
    key = f"budget:{user_id}:{_month_key()}"
    total = r.incrbyfloat(key, request_cost)
    # Keep around enough for monthly checks.
    r.expire(key, 35 * 24 * 3600)
    return float(total)
