# KayGee_1.0 AI Companion
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/vaults data/sessions logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV KAYGEE_DATA_DIR=/app/data
ENV KAYGEE_LOG_DIR=/app/logs

# Expose ports (if needed for future API)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app/src'); from core.protocols import ComponentIdentity; print('OK')" || exit 1

# Default command
CMD ["python", "main.py"]
