from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services.timeline import TimelineService


async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_timeline_service(session: AsyncSession = Depends(get_db)) -> TimelineService:
    return TimelineService(session)


async def optional_password(
    x_timeline_password: str | None = Header(None),
) -> str | None:
    return x_timeline_password
