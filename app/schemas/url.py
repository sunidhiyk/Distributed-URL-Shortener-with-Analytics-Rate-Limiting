from pydantic import BaseModel, HttpUrl
from datetime import datetime


class URLCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = None


class URLResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    click_count: int
    created_at: datetime
    short_url: str

    model_config = {
        "from_attributes": True
    }   

class AnalyticsResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    click_count: int

    model_config = {
        "from_attributes": True
    }     