FROM python:3.11-slim-bookworm

WORKDIR /app

# Install only curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code last for best caching
COPY . .

RUN mkdir -p /tmp/rmapi-uploads

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8001/api/rmapi/health || exit 1

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8001"]
