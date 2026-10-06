# ─────────────────────────────────────────────────────────────
# Order Service — Dockerfile
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose the service port
EXPOSE 8005

# Start the service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
