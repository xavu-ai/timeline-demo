from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TimelineBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    is_public: bool = False
    password: str | None = None


class TimelineCreate(TimelineBase):
    pass


class TimelineUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None


class EntryBase(BaseModel):
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=255)


class EntryCreate(EntryBase):
    pass


class EntryResponse(EntryBase):
    id: str
    timeline_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimelineSummary(BaseModel):
    id: str
    title: str
    description: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    entry_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class TimelineDetail(BaseModel):
    id: str
    title: str
    description: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    entries: list[EntryResponse] = []

    model_config = ConfigDict(from_attributes=True)


class TimelineList(BaseModel):
    items: list[TimelineSummary]
    total: int
    page: int
    limit: int


class PasswordVerify(BaseModel):
    password: str


class AccessTokenResponse(BaseModel):
    access_token: str


class Timeline(TimelineSummary):
    pass
