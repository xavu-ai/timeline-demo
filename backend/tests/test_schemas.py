"""Tests for timeline schemas."""
from datetime import datetime
from app.schemas.timeline import (
    TimelineCreate,
    TimelineSummary,
    TimelineDetail,
    EntryCreate,
    EntryResponse,
    PasswordVerify,
)


def test_timeline_create_valid():
    """Test valid TimelineCreate schema."""
    data = TimelineCreate(
        title="Test Timeline",
        description="A test timeline",
        is_public=True,
        password="secret123",
    )
    assert data.title == "Test Timeline"
    assert data.description == "A test timeline"
    assert data.is_public is True
    assert data.password == "secret123"


def test_timeline_create_minimal():
    """Test TimelineCreate with only required fields."""
    data = TimelineCreate(title="Minimal Timeline")
    assert data.title == "Minimal Timeline"
    assert data.description is None
    assert data.is_public is False
    assert data.password is None


def test_entry_create_valid():
    """Test valid EntryCreate schema."""
    data = EntryCreate(
        content="This is an entry",
        author="Test Author",
    )
    assert data.content == "This is an entry"
    assert data.author == "Test Author"


def test_password_verify():
    """Test PasswordVerify schema."""
    data = PasswordVerify(password="mypassword")
    assert data.password == "mypassword"


def test_timeline_summary_from_orm():
    """Test TimelineSummary with from_attributes."""
    data = TimelineSummary(
        id="123e4567-e89b-12d3-a456-426614174000",
        title="Summary Test",
        description="Test description",
        is_public=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        entry_count=5,
    )
    assert data.id == "123e4567-e89b-12d3-a456-426614174000"
    assert data.entry_count == 5
