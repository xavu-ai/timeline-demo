from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.timeline import Timeline, TimelineEntry  # noqa: E402, F401
