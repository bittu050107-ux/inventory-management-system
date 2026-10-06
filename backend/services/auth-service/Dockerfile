# ─────────────────────────────────────────────────────────────
# Dockerfile — Auth Service
# ─────────────────────────────────────────────────────────────
# Builds a container for the Auth Service.
# Port: 8001
# Run: docker build -t auth-service .
#      docker run -p 8001:8001 --env-file ../../.env auth-service
# ─────────────────────────────────────────────────────────────

# Step 1: Use official Python slim image (smaller footprint than full Python)
FROM python:3.11-slim

# Step 2: Set environment variables
# PYTHONDONTWRITEBYTECODE=1 → Don't create .pyc files (cleaner container)
# PYTHONUNBUFFERED=1        → Print logs immediately (not buffered)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Install system dependencies required by psycopg2
# (PostgreSQL client libraries needed even for binary driver)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy requirements first (Docker layer caching optimization)
# If requirements.txt doesn't change, pip install is cached
COPY requirements.txt .

# Step 6: Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Step 7: Copy the entire application source code
COPY . .

# Step 8: Expose the port this service listens on
EXPOSE 8001

# Step 9: Start the FastAPI application using uvicorn
# --host 0.0.0.0 → Listen on all interfaces (required in Docker)
# --port 8001    → Auth service port
# Remove --reload in production (it's a dev-only feature)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
