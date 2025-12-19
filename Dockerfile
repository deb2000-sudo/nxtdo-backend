# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Final Runtime
FROM python:3.12-slim-bookworm
WORKDIR /app
# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"

# Run the app
CMD ["fastapi", "run", "app/main.py", "--port", "8080", "--host", "0.0.0.0"]