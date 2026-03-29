import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext

from app.models.timeline import Timeline, TimelineEntry
from app.schemas.timeline import (
    TimelineCreate,
    TimelineList,
    TimelineDetail,
    TimelineSummary,
    EntryCreate,
    EntryResponse,
)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TimelineService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_public(self, page: int = 1, limit: int = 20) -> TimelineList:
        offset = (page - 1) * limit

        count_query = select(func.count(Timeline.id)).where(Timeline.is_public)
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Subquery to get entry counts per timeline in a single query
        entry_count_subquery = (
            select(
                TimelineEntry.timeline_id,
                func.count(TimelineEntry.id).label("entry_count")
            )
            .group_by(TimelineEntry.timeline_id)
            .subquery()
        )

        query = (
            select(
                Timeline,
                func.coalesce(entry_count_subquery.c.entry_count, 0).label("entry_count")
            )
            .outerjoin(entry_count_subquery, Timeline.id == entry_count_subquery.c.timeline_id)
            .where(Timeline.is_public)
            .order_by(Timeline.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.all()

        items = [
            TimelineSummary(
                id=timeline.id,
                title=timeline.title,
                description=timeline.description,
                is_public=timeline.is_public,
                created_at=timeline.created_at,
                updated_at=timeline.updated_at,
                entry_count=entry_count,
            )
            for timeline, entry_count in rows
        ]

        return TimelineList(items=items, total=total, page=page, limit=limit)

    async def get_by_id(self, timeline_id: str) -> Timeline | None:
        query = (
            select(Timeline)
            .options(selectinload(Timeline.entries))
            .where(Timeline.id == timeline_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_detail(self, timeline_id: str) -> TimelineDetail | None:
        timeline = await self.get_by_id(timeline_id)
        if not timeline:
            return None

        return TimelineDetail(
            id=timeline.id,
            title=timeline.title,
            description=timeline.description,
            is_public=timeline.is_public,
            created_at=timeline.created_at,
            updated_at=timeline.updated_at,
            entries=[
                EntryResponse(
                    id=e.id,
                    timeline_id=e.timeline_id,
                    content=e.content,
                    author=e.author,
                    created_at=e.created_at,
                )
                for e in timeline.entries
            ],
        )

    def hash_password(self, password: str) -> str:
        return _pwd_context.hash(password)

    async def create(self, data: TimelineCreate) -> Timeline:
        timeline = Timeline(
            id=str(uuid.uuid4()),
            title=data.title,
            description=data.description,
            is_public=data.is_public,
            password_hash=self.hash_password(data.password) if data.password else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(timeline)
        await self.session.commit()
        await self.session.refresh(timeline)
        return timeline

    async def create_entry(self, timeline_id: str, data: EntryCreate) -> TimelineEntry:
        entry = TimelineEntry(
            id=str(uuid.uuid4()),
            timeline_id=timeline_id,
            content=data.content,
            author=data.author,
            created_at=datetime.utcnow(),
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def verify_password(self, timeline_id: str, password: str) -> bool:
        query = select(Timeline).where(Timeline.id == timeline_id)
        result = await self.session.execute(query)
        timeline = result.scalar_one_or_none()
        if not timeline:
            return False
        if not timeline.password_hash:
            return False
        return _pwd_context.verify(password, timeline.password_hash)

    async def generate_access_token(self, timeline_id: str) -> str:
        return f"tl_{timeline_id}_{uuid.uuid4().hex[:16]}"

    def to_summary(self, timeline: Timeline, entry_count: int = 0) -> TimelineSummary:
        return TimelineSummary(
            id=timeline.id,
            title=timeline.title,
            description=timeline.description,
            is_public=timeline.is_public,
            created_at=timeline.created_at,
            updated_at=timeline.updated_at,
            entry_count=entry_count,
        )
