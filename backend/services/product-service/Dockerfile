# ─────────────────────────────────────────────────────────────
# Product Service — Dockerfile
# ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for psycopg2 if building from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service application code
COPY . .

# Expose Product Service port
EXPOSE 8003

# Run service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
