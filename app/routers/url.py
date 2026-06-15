from fastapi import APIRouter, Depends, HTTPException
import re
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.url import URLCreate, URLResponse, AnalyticsResponse
from app.models.url import URL
from app.oauth2 import get_current_user
from app.utils import generate_short_code

router = APIRouter(
    prefix="/urls",
    tags=["URLs"]
)

RESERVED_ALIASES = {
    "auth",
    "urls",
    "docs",
    "redoc",
    "openapi.json"
}


@router.get("/")
def get_my_urls(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    urls = db.query(URL).filter(
        URL.user_id == current_user.id
    ).all()

    return urls



@router.post(
    "/shorten",
    response_model=URLResponse
)
def shorten_url(
    url: URLCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if url.custom_alias:
        if not re.fullmatch(
        r"[A-Za-z0-9_-]+",
        url.custom_alias
    ):
          raise HTTPException(
            status_code=400,
            detail="Invalid alias"
        )

        if url.custom_alias.lower() in RESERVED_ALIASES:
            raise HTTPException(
            status_code=400,
            detail="Reserved alias"
        ) 

        existing = db.query(URL).filter(
            URL.short_code == url.custom_alias
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Alias already exists"
            )

        short_code = url.custom_alias

    else:

        short_code = generate_short_code()

        while db.query(URL).filter(
            URL.short_code == short_code
        ).first():

            short_code = generate_short_code()

    # <- OUTSIDE if/else

    new_url = URL(
        original_url=str(url.original_url),
        short_code=short_code,
        user_id=current_user.id
    )

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {
    "id": new_url.id,
    "original_url": new_url.original_url,
    "short_code": new_url.short_code,
    "click_count": new_url.click_count,
    "created_at": new_url.created_at,
    "short_url": f"http://127.0.0.1:8000/{new_url.short_code}"
}



@router.get("/{id}/analytics",response_model=AnalyticsResponse)
def get_analytics(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    url = db.query(URL).filter(
        URL.id == id
    ).first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return url



@router.delete("/{id}")
def delete_url(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    url_query = db.query(URL).filter(
        URL.id == id
    )

    url = url_query.first()

    if not url:
        raise HTTPException(
            status_code=404,
            detail="URL not found"
        )

    if url.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    url_query.delete(
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "URL deleted"
    }


