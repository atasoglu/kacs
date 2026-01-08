FROM python:3.10-slim

# Install git (required for git operations)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install package
COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

# Set git safe directory for CI/CD (allow all directories)
RUN git config --global --add safe.directory '*'

CMD ["kacs"]
