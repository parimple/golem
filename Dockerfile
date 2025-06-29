# GOLEM Discord Bot Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 golem && \
    chown -R golem:golem /app

# Switch to non-root user
USER golem

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import discord; print('healthy')" || exit 1

# Default environment
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Run the bot
CMD ["python", "run.py"]