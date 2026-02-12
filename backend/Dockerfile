# Use Python 3.11 image
FROM python:3.11-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright and ImageMagick
RUN apt-get update && apt-get install -y \
  wget \
  gnupg \
  unzip \
  curl \
  ca-certificates \
  imagemagick \
  inkscape \
  libgbm1 \
  libasound2 \
  && rm -rf /var/lib/apt/lists/*

# Relax the PDF/PS/EPS/XPS policy for whichever IM version is present
RUN set -eux; \
  POLICY_FILE=""; \
  if [ -f /etc/ImageMagick-7/policy.xml ]; then POLICY_FILE=/etc/ImageMagick-7/policy.xml; \
  elif [ -f /etc/ImageMagick-6/policy.xml ]; then POLICY_FILE=/etc/ImageMagick-6/policy.xml; \
  elif [ -f /etc/ImageMagick/policy.xml ]; then POLICY_FILE=/etc/ImageMagick/policy.xml; \
  fi; \
  echo "Using policy file: ${POLICY_FILE:-<none>}"; \
  if [ -n "$POLICY_FILE" ]; then \
  # If the deny rules exist, flip them; otherwise append allow rules.
  sed -i -E 's/rights="none" pattern="(PDF|PS|EPS|XPS)"/rights="read|write" pattern="\1"/g' "$POLICY_FILE" || true; \
  grep -q 'pattern="PDF"' "$POLICY_FILE" || { \
  awk 'BEGIN{print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<policymap>"} 1 END{print "  <policy domain=\"coder\" rights=\"read|write\" pattern=\"PDF\"/>\n  <policy domain=\"coder\" rights=\"read|write\" pattern=\"PS\"/>\n  <policy domain=\"coder\" rights=\"read|write\" pattern=\"EPS\"/>\n  <policy domain=\"coder\" rights=\"read|write\" pattern=\"XPS\"/>\n</policymap>"}' \
  > "$POLICY_FILE"; \
  }; \
  else \
  echo "WARNING: No ImageMagick policy.xml found."; \
  fi

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium && \
  playwright install-deps chromium

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p input output

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
