import json
import logging
import signal
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import redis
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import check_budget, record_usage
from app.rate_limiter import check_rate_limit
from utils.mock_llm import ask as llm_ask

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger("agent")

r = redis.from_url(settings.redis_url, decode_responses=True)
START_TS = time.time()
READY = False


def _log(event: str, **kwargs) -> None:
    payload = {"event": event, "ts": datetime.now(timezone.utc).isoformat(), **kwargs}
    logger.info(json.dumps(payload))


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str = Field(..., min_length=1, max_length=128)


class AskResponse(BaseModel):
    answer: str
    conversation_length: int
    monthly_spent_usd: float


@asynccontextmanager
async def lifespan(app: FastAPI):
    global READY
    try:
        r.ping()
        READY = True
        _log("startup", status="ready")
        yield
    finally:
        READY = False
        _log("shutdown")


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "uptime_seconds": round(time.time() - START_TS, 2),
    }


@app.get("/ready")
def ready():
    if not READY:
        raise HTTPException(status_code=503, detail="Service not ready")
    try:
        r.ping()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc
    return {"ready": True}


@app.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    request: Request,
    _api_user: str = Depends(verify_api_key),
):
    check_rate_limit(body.user_id)
    check_budget(body.user_id)

    history_key = f"conversation:{body.user_id}"
    history = r.lrange(history_key, 0, -1)

    prompt = body.question
    if history:
        prompt = f"History:\n" + "\n".join(history[-10:]) + f"\nQuestion: {body.question}"
    answer = llm_ask(prompt)

    r.rpush(history_key, f"User: {body.question}")
    r.rpush(history_key, f"Assistant: {answer}")
    r.expire(history_key, settings.conversation_ttl_seconds)
    conversation_length = r.llen(history_key)

    spent = record_usage(body.user_id, settings.estimated_cost_per_request_usd)
    _log(
        "ask",
        client=str(request.client.host) if request.client else "unknown",
        user_id=body.user_id,
        conversation_length=conversation_length,
        spent_month_usd=round(spent, 4),
    )

    return AskResponse(
        answer=answer,
        conversation_length=conversation_length,
        monthly_spent_usd=round(spent, 4),
    )


def _handle_sigterm(signum, frame):  # noqa: ANN001, ARG001
    _log("signal", signum=signum)


signal.signal(signal.SIGTERM, _handle_sigterm)
