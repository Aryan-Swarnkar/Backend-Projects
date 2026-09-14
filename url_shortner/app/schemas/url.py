from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class CreateURLRequest(BaseModel):
    original_url: AnyHttpUrl
    expires_at: datetime | None = None


class URLResponse(BaseModel):
    id: int
    short_code: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None
    click_count: int

    model_config = {
        "from_attributes": True,
    }