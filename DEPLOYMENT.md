# Deployment Guide

## Automatic Deployment via GitHub Actions

The repository is configured for automatic deployment with GitHub Actions.

### Services Routing

- `https://garden.timosur.com/` → Frontend
- `https://garden.timosur.com/api/` → Backend
- `https://garden.timosur.com/rmapi/` → rmapi-wrapper

### Initial Setup

1. **Prepare the server:**

   ```bash
   # Point domain DNS to server IP
   # Open ports 80 and 443 in the firewall
   ```

2. **Configure GitHub Secrets:**
   The following secrets must be set in the GitHub repository settings:

   - `OPENAI_API_KEY`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`

3. **Set up self-hosted runner:**
   Set up a GitHub Actions self-hosted runner on the target server.

4. **Automatic deployment:**
   On every push to the `main` branch, deployment happens automatically:
   - SSL certificates are initialized automatically on first deployment
   - Services are built and started
   - On subsequent deployments, existing certificates are reused

### Manual Deployment

If you want to deploy manually:

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd life-as-a-garden
   ```

2. **Create environment files:**

   ```bash
   # Backend .env
   cat > backend/.env << EOF
   OPENAI_API_KEY=your_openai_key
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_smtp_username
   SMTP_PASSWORD=your_smtp_password
   NOTIFICATION_EMAIL=lebensgarten@timosur.com
   EMAIL_NOTIFICATIONS_ENABLED=true
   EOF

   # Frontend .env
   cat > garden/.env << EOF
   VITE_API_BASE_URL=https://garden.timosur.com/api
   EOF
   ```

3. **Initialize SSL certificates (only the first time):**

   ```bash
   chmod +x init-letsencrypt.sh
   ./init-letsencrypt.sh
   ```

4. **Start services:**

   ```bash
   docker-compose up -d --build
   ```

### Deploy updates:

```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### View logs:

```bash
# All services
docker-compose logs -f

# Specific services
docker-compose logs -f nginx
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f rmapi-wrapper
```

### Renew SSL certificate:

The certificate is automatically checked and renewed every 12 hours by the certbot container.

Manual renewal:

```bash
docker-compose exec certbot certbot renew
docker-compose exec nginx nginx -s reload
```

## Local Development

For local development, you can start the services directly without using Docker Compose.

If you want to use Docker Compose locally, use `nginx.dev.conf` for HTTP without SSL:

```bash
# In docker-compose.yml, adjust the nginx volumes:
volumes:
  - ./nginx/nginx.dev.conf:/etc/nginx/nginx.conf
  - ./certbot/conf:/etc/letsencrypt
  - ./certbot/www:/var/www/certbot
```
