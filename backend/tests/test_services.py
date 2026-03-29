"""Tests for timeline services."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.timeline import TimelineService


class TestTimelineService:
    """Test TimelineService methods."""

    def test_hash_password(self):
        """Test password hashing."""
        mock_session = MagicMock()
        service = TimelineService(mock_session)

        hash1 = service.hash_password("password123")
        hash2 = service.hash_password("password123")

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64 hex chars
        assert hash1 != "password123"

    def test_to_summary(self):
        """Test converting Timeline to TimelineSummary."""
        mock_session = MagicMock()
        service = TimelineService(mock_session)

        mock_timeline = MagicMock()
        mock_timeline.id = "123e4567-e89b-12d3-a456-426614174000"
        mock_timeline.title = "Test Timeline"
        mock_timeline.description = "Test description"
        mock_timeline.is_public = True
        mock_timeline.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_timeline.updated_at = datetime(2024, 1, 1, 12, 0, 0)

        summary = service.to_summary(mock_timeline, entry_count=10)

        assert summary.id == "123e4567-e89b-12d3-a456-426614174000"
        assert summary.title == "Test Timeline"
        assert summary.description == "Test description"
        assert summary.is_public is True
        assert summary.entry_count == 10

    @pytest.mark.asyncio
    async def test_verify_password_correct(self):
        """Test password verification with correct password."""
        mock_session = AsyncMock()
        service = TimelineService(mock_session)

        mock_timeline = MagicMock()
        mock_timeline.password_hash = service.hash_password("correct_password")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_timeline
        mock_session.execute.return_value = mock_result

        result = await service.verify_password("timeline_id", "correct_password")
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_password_wrong(self):
        """Test password verification with wrong password."""
        mock_session = AsyncMock()
        service = TimelineService(mock_session)

        mock_timeline = MagicMock()
        mock_timeline.password_hash = service.hash_password("correct_password")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_timeline
        mock_session.execute.return_value = mock_result

        result = await service.verify_password("timeline_id", "wrong_password")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_password_no_hash(self):
        """Test password verification when no password set."""
        mock_session = AsyncMock()
        service = TimelineService(mock_session)

        mock_timeline = MagicMock()
        mock_timeline.password_hash = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_timeline
        mock_session.execute.return_value = mock_result

        result = await service.verify_password("timeline_id", "any_password")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_password_timeline_not_found(self):
        """Test password verification when timeline not found."""
        mock_session = AsyncMock()
        service = TimelineService(mock_session)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await service.verify_password("nonexistent_id", "any_password")
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_access_token(self):
        """Test access token generation."""
        mock_session = MagicMock()
        service = TimelineService(mock_session)

        timeline_id = "123e4567-e89b-12d3-a456-426614174000"
        token = await service.generate_access_token(timeline_id)

        assert token.startswith("tl_123e4567-e89b-12d3-a456-426614174000_")
        assert len(token) == len(f"tl_{timeline_id}_") + 16
