# Uses Ubuntu Jammy with all Playwright bits preinstalled (ARM64 supported)
FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

# Optional: tools you still need
RUN apt-get update && apt-get install -y \
    imagemagick inkscape \
  && rm -rf /var/lib/apt/lists/*

# If you must relax ImageMagick PDF policy (be aware of security implications)
RUN POLICY_FILE=$(find /etc -name "policy.xml" -path "*/ImageMagick*" 2>/dev/null | head -1) && \
    if [ -n "$POLICY_FILE" ]; then \
      sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' "$POLICY_FILE" && \
      sed -i 's/rights="none" pattern="PS"/rights="read|write" pattern="PS"/' "$POLICY_FILE" && \
      sed -i 's/rights="none" pattern="EPS"/rights="read|write" pattern="EPS"/' "$POLICY_FILE" && \
      sed -i 's/rights="none" pattern="XPS"/rights="read|write" pattern="XPS"/' "$POLICY_FILE"; \
    fi

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p input output db

EXPOSE 8000
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
