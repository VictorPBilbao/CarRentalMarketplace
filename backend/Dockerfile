FROM python:3.12-slim

# Copy the uv binary directly from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency definition files first (for caching layer)
COPY pyproject.toml uv.lock ./

# Install dependencies directly into the system python
RUN uv sync

# Copy the rest of the application
COPY . .

# By default, start with fastapi dev for hot reloading
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
