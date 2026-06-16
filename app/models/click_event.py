from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql.expression import text

from app.database import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(
        Integer,
        primary_key=True,
        nullable=False
    )

    url_id = Column(
        Integer,
        ForeignKey(
            "urls.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    ip_address = Column(
        String,
        nullable=False
    )

    user_agent = Column(
        String,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()")
    )