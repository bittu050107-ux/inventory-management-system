# ─────────────────────────────────────────────────────────────
# Dockerfile — API Gateway
# ─────────────────────────────────────────────────────────────
# Builds a container for the API Gateway service.
# Port: 8000
# Run:
#   docker build -t api-gateway .
#   docker run -p 8000:8000 --env-file ../../.env api-gateway
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependencies first to leverage Docker layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
