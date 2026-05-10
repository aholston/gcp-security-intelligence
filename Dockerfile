FROM python:3.13-slim

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency manifest first so this layer is cached on code-only changes
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

# Cloud Run injects PORT; default to 8080 for local dev
ENV PORT=8080

EXPOSE ${PORT}

# Non-root user for least-privilege execution
RUN useradd --no-create-home --shell /bin/false appuser
USER appuser

# Update this CMD once you've defined your Cloud Run HTTP entrypoint in main.py
CMD ["sh", "-c", "uv run uvicorn gcp_security_intelligence.main:app --host 0.0.0.0 --port ${PORT}"]
