FROM python:3.10-slim

# Install git (required for git operations)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy and install package
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

# Set git safe directory for CI/CD
RUN git config --global --add safe.directory /workspace

CMD ["kacs"]
