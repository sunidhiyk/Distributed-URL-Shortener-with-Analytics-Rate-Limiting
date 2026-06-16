import json
from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from app.routers import auth, url
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.url import URL
from app.redis_client import redis_client
from app.middleware.rate_limit import rate_limiter
from app.models.click_event import ClickEvent
from app.services.analytics import track_click

app = FastAPI()

app.include_router(auth.router)
app.include_router(url.router)


@app.get("/")
def root():
    return {"message": "URL Shortener API"}


@app.get("/test-limit")
def test_limit(
    _: None = Depends(rate_limiter)
):
    return {"message": "ok"}



@app.get("/redis-test")
def redis_test():

    redis_client.set(
        "hello",
        "world"
    )

    return {
        "value": redis_client.get("hello")
    }



@app.get("/{short_code}")
def redirect_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):

    cached_data = redis_client.get(short_code)

    if cached_data:

      print("CACHE HIT")

      try:
         data = json.loads(cached_data)

      except json.JSONDecodeError:

         redis_client.delete(short_code)

         raise HTTPException(
            status_code=500,
            detail="Invalid cache data"
    )

      background_tasks.add_task(
        track_click,
        data["id"],
        request.client.host,
        request.headers.get("user-agent")
    )

      return RedirectResponse(
        url=data["original_url"]
    )

    print("CACHE MISS")

    url = db.query(URL).filter(
        URL.short_code == short_code).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    
    redis_client.setex(
    short_code,
    3600,
    json.dumps({
        "id": url.id,
        "original_url": url.original_url
    })
)
    

    background_tasks.add_task(
    track_click,
    url.id,
    request.client.host,
    request.headers.get("user-agent")
)

    return RedirectResponse(
        url=url.original_url
    )


