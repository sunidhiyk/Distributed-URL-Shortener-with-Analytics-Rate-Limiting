from fastapi import Request, HTTPException, Response
from app.redis_client import redis_client

RATE_LIMIT = 100
WINDOW = 60


def rate_limiter(request: Request, response:  Response):

    ip = request.client.host

    key = f"rate_limit:{ip}"

    current = redis_client.get(key)

    if current is None:

        redis_client.setex(
            key,
            WINDOW,
            1
        )

        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = str(RATE_LIMIT - 1)

        return

        

    current = int(current)

    if current >= RATE_LIMIT:

        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )

    redis_client.incr(key)

    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(
        RATE_LIMIT - current - 1
    )