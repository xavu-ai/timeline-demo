FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY . .
RUN uv sync --frozen

FROM python:3.11-slim
WORKDIR /app
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser . /app
USER appuser
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 6100
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6100"]
