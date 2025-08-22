# Use Python 3.11 image
FROM python:3.11

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

# Configure ImageMagick policy to allow PDF reading
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-7/policy.xml && \
  sed -i 's/rights="none" pattern="PS"/rights="read|write" pattern="PS"/' /etc/ImageMagick-7/policy.xml && \
  sed -i 's/rights="none" pattern="EPS"/rights="read|write" pattern="EPS"/' /etc/ImageMagick-7/policy.xml && \
  sed -i 's/rights="none" pattern="XPS"/rights="read|write" pattern="XPS"/' /etc/ImageMagick-7/policy.xml

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
RUN mkdir -p input output db

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
