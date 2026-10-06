from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field

class SiteCreate(BaseModel):
    workspace_id: int = 1
    name: str = Field(min_length=1, max_length=160)
    url: HttpUrl

class KeywordCreate(BaseModel):
    site_id: int
    keyword: str
    target_url: HttpUrl | None = None
    country: str = "US"
    device: str = "desktop"

class DataState(BaseModel):
    status: str
    source: str
    last_successful_at: datetime | None
    value: object | None
    error: str | None = None
