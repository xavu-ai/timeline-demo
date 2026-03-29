# Project Name

Full-stack application built with FastAPI + Next.js.

## Stack

| Component | Technology | Port |
|-----------|-----------|------|
| Backend | FastAPI + Python 3.11 + SQLAlchemy 2.0 | 6100 |
| Frontend | Next.js 14 + React 18 + TypeScript 5 + Tailwind CSS 4 | 8100 |
| Database | PostgreSQL 16 | 5432 |

## Quick Start

```bash
# Copy environment variables
cp .env.example .env

# Start all services
docker compose up --build

# Access the app
# Frontend: http://localhost:8100
# Backend:  http://localhost:6100
# API docs: http://localhost:6100/docs
```

## Development

### Backend

```bash
cd backend
pip install uv
uv sync
uv run uvicorn app.main:app --reload --port 6100
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

### Run Tests

```bash
# Backend tests
cd backend && uv run pytest

# Integration tests (Docker)
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## Architecture

- Frontend communicates with backend via `/api` proxy (Next.js rewrites)
- No `NEXT_PUBLIC_` environment variables for API URLs
- Backend uses Pydantic Settings for configuration
- Multi-stage Docker builds for production
- PostgreSQL managed via SQLAlchemy 2.0

## Deployment

Automated via GitHub Actions → Azure Container Apps.

- **Staging**: Deploys on every push to `main`
- **Production**: Requires staging health checks to pass

See [.github/workflows/deploy.yml](.github/workflows/deploy.yml).
