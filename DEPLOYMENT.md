# Deployment Setup

This repository includes automated deployment using GitHub Actions and a scheduled watering system.

## GitHub Actions Deployment

The deployment workflow (`.github/workflows/deploy.yml`) automatically deploys the application when changes are pushed to the main branch.

### Prerequisites for Self-Hosted Runner

1. **Set up a self-hosted runner** on your Linux machine:

   ```bash
   # Follow GitHub's instructions to add a self-hosted runner
   # https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners
   ```

2. **Install Docker and Docker Compose** on the runner machine:

   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Configure GitHub Secrets**:
   Add any required environment variables as GitHub secrets:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add secrets like `OPENAI_API_KEY`, `REMARKABLE_TOKEN`, etc.

### Deployment Process

The workflow will:

1. Checkout the latest code
2. Create environment files from GitHub secrets
3. Stop existing containers
4. Build and start new containers
5. Verify the deployment
6. Show logs if deployment fails

## Automatic Watering Schedule

The docker-compose file includes a `scheduler` service that automatically triggers the watering endpoint every night at 1 AM CET.

### Scheduler Details

- **Container**: `garden-scheduler`
- **Image**: `curlimages/curl:latest` with supercronic
- **Schedule**: `0 1 * * *` (1 AM CET daily)
- **Endpoint**: `POST http://backend:8000/api/garden/water`
- **Timezone**: Europe/Berlin (CET)

### Manual Deployment

To deploy manually:

```bash
# Clone the repository
git clone <your-repo-url>
cd life-as-a-garden

# Create backend environment file
mkdir -p backend
cat > backend/.env << EOF
# Add your environment variables
OPENAI_API_KEY=your_key_here
REMARKABLE_TOKEN=your_token_here
EOF

# Deploy with Docker Compose
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs -f
```

### Service URLs

After deployment, the following services will be available:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RMAPI Wrapper**: http://localhost:8001

### Monitoring

- View logs: `docker-compose logs -f [service-name]`
- Check status: `docker-compose ps`
- Restart services: `docker-compose restart [service-name]`
- Stop all: `docker-compose down`

### Troubleshooting

1. **Scheduler not working**: Check scheduler logs with `docker-compose logs scheduler`
2. **Services not starting**: Check individual service logs
3. **Network issues**: Ensure all services are on the same Docker network
4. **Permission issues**: Ensure the runner user has Docker permissions
