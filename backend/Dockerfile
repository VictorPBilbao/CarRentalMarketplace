# Use the Python 3.14 release candidate to match the pyproject.toml requires-python
FROM python:3.14-slim-bookworm

# Copy the uv binary from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Enable bytecode compilation to improve startup time
ENV UV_COMPILE_BYTECODE=1

# Copy the lockfile and pyproject.toml first for optimal layer caching
COPY uv.lock pyproject.toml ./

# Install dependencies using uv.
# We create a virtual environment inside the container automatically via uv sync.
# --frozen ensures we don't accidentally update uv.lock during building.
# --no-dev ensures we only install production dependencies.
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code
COPY . .

# Sync again to install the project itself (if applicable)
RUN uv sync --frozen --no-dev

# Expose the port that FastAPI will run on
EXPOSE 8000

# Put the virtual environment in the PATH so we can run 'fastapi' directly
ENV PATH="/app/.venv/bin:$PATH"

# Start the FastAPI application
CMD ["fastapi", "run", "main.py", "--port", "8000", "--host", "0.0.0.0"]
