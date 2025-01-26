# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install git and other necessary packages
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -r requirements.txt

ADD . /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# RUN /bin/bash scripts/download_models.sh

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
# Uses `fastapi dev` to enable hot-reloading when the `watch` sync occurs
# Uses `--host 0.0.0.0` to allow access from outside the container
CMD ["/bin/bash"]