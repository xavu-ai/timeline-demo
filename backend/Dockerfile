# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
COPY .python-version .
RUN uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev
COPY . .

# Stage 2: Production
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app /app
EXPOSE 6100
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6100"]
