# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install git and other necessary packages
RUN apt-get update && \
    apt-get install -y git libgomp1 && \
    # apt-get install -y git wget dpkg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
# RUN dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb


# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Installing separately from its dependencies allows optimal layer caching
# Install the project's dependencies using the lockfile and settings
# Copy requirements first
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . .

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Mount AWS credentials for donwloading models from S3
RUN --mount=type=secret,id=aws_credentials,target=/root/.aws/credentials \
    /bin/bash scripts/download_models.sh

# Expose port
EXPOSE 8001

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Start Gunicorn with Uvicorn workers
CMD ["gunicorn", \
    "--bind", "0.0.0.0:8001", \
    "--workers", "1", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--timeout", "300", \
    "ocr_api.asgi:application"]