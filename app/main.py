from fastapi import FastAPI, Depends, HTTPException
from app.routers import auth, url
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.url import URL

app = FastAPI()

app.include_router(auth.router)
app.include_router(url.router)


@app.get("/")
def root():
    return {"message": "URL Shortener API"}

@app.get("/{short_code}")
def redirect_url(
    short_code: str,
    db: Session = Depends(get_db)
):

    url = db.query(URL).filter(
        URL.short_code == short_code
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )
    
    url.click_count += 1

    db.commit()

    return RedirectResponse(
        url=url.original_url
    )