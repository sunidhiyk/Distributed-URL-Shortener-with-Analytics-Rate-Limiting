from app.database import SessionLocal
from app.models.click_event import ClickEvent
from app.models.url import URL


def track_click(
    url_id: int,
    ip_address: str,
    user_agent: str | None
):

    db = SessionLocal()

    try:
        print(f"Tracking click for URL {url_id}")

        click_event = ClickEvent(
            url_id=url_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(click_event)

        url = db.query(URL).filter(
            URL.id == url_id
        ).first()

        if url:
            url.click_count += 1

        db.commit()
        print("Click tracked successfully")
        

    except Exception as e:
        print(f"Error tracking click: {e}")
        db.rollback()

    finally:
        db.close()