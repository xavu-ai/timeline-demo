from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_timeline_service, optional_password
from app.schemas.timeline import (
    TimelineCreate,
    TimelineList,
    TimelineDetail,
    Timeline,
    EntryCreate,
    EntryResponse,
    PasswordVerify,
    AccessTokenResponse,
)
from app.services.timeline import TimelineService

router = APIRouter(prefix="/api/timelines", tags=["timelines"])


@router.get("/public", response_model=TimelineList)
async def list_public_timelines(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineList:
    return await service.list_public(page, limit)


@router.get("/{timeline_id}", response_model=TimelineDetail)
async def get_timeline(
    timeline_id: str,
    x_timeline_password: str | None = Depends(optional_password),
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineDetail:
    timeline = await service.get_detail(timeline_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    if timeline.password_hash and not x_timeline_password:
        raise HTTPException(status_code=403, detail="Password required")

    if timeline.password_hash and x_timeline_password:
        if not await service.verify_password(timeline_id, x_timeline_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

    return timeline


@router.post("", response_model=Timeline)
async def create_timeline(
    data: TimelineCreate,
    service: TimelineService = Depends(get_timeline_service),
) -> Timeline:
    timeline = await service.create(data)
    return service.to_summary(timeline, 0)


@router.post("/{timeline_id}/entries", response_model=EntryResponse)
async def create_entry(
    timeline_id: str,
    data: EntryCreate,
    service: TimelineService = Depends(get_timeline_service),
) -> EntryResponse:
    timeline = await service.get_by_id(timeline_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    entry = await service.create_entry(timeline_id, data)
    return EntryResponse(
        id=entry.id,
        timeline_id=entry.timeline_id,
        content=entry.content,
        author=entry.author,
        created_at=entry.created_at,
    )


@router.post("/{timeline_id}/verify", response_model=AccessTokenResponse)
async def verify_password(
    timeline_id: str,
    data: PasswordVerify,
    service: TimelineService = Depends(get_timeline_service),
) -> AccessTokenResponse:
    timeline = await service.get_by_id(timeline_id)
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline not found")

    if not await service.verify_password(timeline_id, data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = await service.generate_access_token(timeline_id)
    return AccessTokenResponse(access_token=token)
