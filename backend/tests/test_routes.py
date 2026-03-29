"""Tests for timeline routes."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestHealthEndpoint:
    """Tests for /healthz endpoint."""

    @pytest.mark.asyncio
    async def test_healthz_returns_ok(self, client):
        """Test health check returns ok status."""
        response = await client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestPublicTimelinesEndpoint:
    """Tests for GET /api/timelines/public endpoint."""

    @pytest.mark.asyncio
    async def test_list_public_timelines_empty(self, client):
        """Test listing public timelines when none exist."""
        with patch("app.services.timeline.TimelineService.list_public") as mock_list:
            mock_list.return_value = MagicMock(
                items=[],
                total=0,
                page=1,
                limit=20,
            )
            response = await client.get("/api/timelines/public")
            assert response.status_code == 200
            data = response.json()
            assert data["items"] == []
            assert data["total"] == 0
            assert data["page"] == 1
            assert data["limit"] == 20


class TestGetTimelineEndpoint:
    """Tests for GET /api/timelines/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_timeline_not_found(self, client):
        """Test getting a timeline that doesn't exist."""
        with patch("app.services.timeline.TimelineService.get_detail") as mock_get:
            mock_get.return_value = None
            response = await client.get("/api/timelines/nonexistent-id")
            assert response.status_code == 404
            assert response.json() == {"detail": "Timeline not found"}

    @pytest.mark.asyncio
    async def test_get_timeline_protected_no_password(self, client):
        """Test accessing protected timeline without password."""
        mock_timeline = MagicMock()
        mock_timeline.password_hash = "somehash"

        with patch("app.services.timeline.TimelineService.get_detail") as mock_get:
            mock_get.return_value = MagicMock(
                id="test-id",
                title="Protected",
                description=None,
                is_public=False,
                password_hash="somehash",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                entries=[],
            )
            response = await client.get("/api/timelines/test-id")
            assert response.status_code == 403
            assert response.json() == {"detail": "Password required"}


class TestVerifyPasswordEndpoint:
    """Tests for POST /api/timelines/{id}/verify endpoint."""

    @pytest.mark.asyncio
    async def test_verify_password_wrong(self, client):
        """Test verifying wrong password returns 401."""
        with patch("app.services.timeline.TimelineService.get_by_id") as mock_get, \
             patch("app.services.timeline.TimelineService.verify_password") as mock_verify:
            mock_get.return_value = MagicMock(id="test-id")
            mock_verify.return_value = False

            response = await client.post(
                "/api/timelines/test-id/verify",
                json={"password": "wrong_password"},
            )
            assert response.status_code == 401
            assert response.json() == {"detail": "Invalid credentials"}

    @pytest.mark.asyncio
    async def test_verify_password_correct(self, client):
        """Test verifying correct password returns token."""
        with patch("app.services.timeline.TimelineService.get_by_id") as mock_get, \
             patch("app.services.timeline.TimelineService.verify_password") as mock_verify, \
             patch("app.services.timeline.TimelineService.generate_access_token") as mock_token:
            mock_get.return_value = MagicMock(id="test-id")
            mock_verify.return_value = True
            mock_token.return_value = "tl_test-id_abc123def456"

            response = await client.post(
                "/api/timelines/test-id/verify",
                json={"password": "correct_password"},
            )
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["access_token"] == "tl_test-id_abc123def456"

    @pytest.mark.asyncio
    async def test_verify_password_timeline_not_found(self, client):
        """Test verifying password for nonexistent timeline."""
        with patch("app.services.timeline.TimelineService.get_by_id") as mock_get:
            mock_get.return_value = None

            response = await client.post(
                "/api/timelines/nonexistent-id/verify",
                json={"password": "any_password"},
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "Timeline not found"}


class TestCreateTimelineEndpoint:
    """Tests for POST /api/timelines endpoint."""

    @pytest.mark.asyncio
    async def test_create_timeline(self, client):
        """Test creating a new timeline."""
        mock_timeline = MagicMock()
        mock_timeline.id = "new-timeline-id"
        mock_timeline.title = "New Timeline"
        mock_timeline.description = "Test description"
        mock_timeline.is_public = True
        mock_timeline.created_at = datetime.utcnow()
        mock_timeline.updated_at = datetime.utcnow()

        with patch("app.services.timeline.TimelineService.create") as mock_create, \
             patch("app.services.timeline.TimelineService.to_summary") as mock_summary:
            mock_create.return_value = mock_timeline
            mock_summary.return_value = MagicMock(
                id="new-timeline-id",
                title="New Timeline",
                description="Test description",
                is_public=True,
                created_at=mock_timeline.created_at,
                updated_at=mock_timeline.updated_at,
                entry_count=0,
            )

            response = await client.post(
                "/api/timelines",
                json={
                    "title": "New Timeline",
                    "description": "Test description",
                    "is_public": True,
                },
            )
            assert response.status_code == 200


class TestCreateEntryEndpoint:
    """Tests for POST /api/timelines/{id}/entries endpoint."""

    @pytest.mark.asyncio
    async def test_create_entry_timeline_not_found(self, client):
        """Test creating entry for nonexistent timeline."""
        with patch("app.services.timeline.TimelineService.get_by_id") as mock_get:
            mock_get.return_value = None

            response = await client.post(
                "/api/timelines/nonexistent-id/entries",
                json={"content": "Test entry", "author": "Test Author"},
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "Timeline not found"}

    @pytest.mark.asyncio
    async def test_create_entry_success(self, client):
        """Test creating an entry successfully."""
        mock_timeline = MagicMock()
        mock_entry = MagicMock()
        mock_entry.id = "new-entry-id"
        mock_entry.timeline_id = "test-timeline-id"
        mock_entry.content = "Test entry content"
        mock_entry.author = "Test Author"
        mock_entry.created_at = datetime.utcnow()

        with patch("app.services.timeline.TimelineService.get_by_id") as mock_get, \
             patch("app.services.timeline.TimelineService.create_entry") as mock_create:
            mock_get.return_value = mock_timeline
            mock_create.return_value = mock_entry

            response = await client.post(
                "/api/timelines/test-timeline-id/entries",
                json={"content": "Test entry content", "author": "Test Author"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "new-entry-id"
            assert data["content"] == "Test entry content"
            assert data["author"] == "Test Author"
