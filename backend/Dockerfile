# ---- Stage 1: Install Python deps + Playwright ----
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install build-time deps for pip packages that compile C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (cached unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Runtime ----
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Install only runtime system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
  imagemagick \
  inkscape \
  libgbm1 \
  libasound2 \
  libpq5 \
  ca-certificates \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Relax the PDF/PS/EPS/XPS ImageMagick policy
RUN set -eux; \
  POLICY_FILE=""; \
  if [ -f /etc/ImageMagick-7/policy.xml ]; then POLICY_FILE=/etc/ImageMagick-7/policy.xml; \
  elif [ -f /etc/ImageMagick-6/policy.xml ]; then POLICY_FILE=/etc/ImageMagick-6/policy.xml; \
  elif [ -f /etc/ImageMagick/policy.xml ]; then POLICY_FILE=/etc/ImageMagick/policy.xml; \
  fi; \
  if [ -n "$POLICY_FILE" ]; then \
  sed -i -E 's/rights="none" pattern="(PDF|PS|EPS|XPS)"/rights="read|write" pattern="\1"/g' "$POLICY_FILE" || true; \
  fi

# Install Playwright Chromium (large + stable — cached unless pip deps change)
RUN playwright install chromium && \
  playwright install-deps chromium && \
  rm -rf /var/lib/apt/lists/*

# Copy application code (changes most often — last for best caching)
COPY . .

# Create necessary directories
RUN mkdir -p input output

EXPOSE 8000

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
