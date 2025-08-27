# Life as a Garden - Frontend

This is the frontend React application for the Life as a Garden project, built with React + TypeScript + Vite.

## Environment Configuration

The application uses environment variables to configure the API base URL for different deployment scenarios:

### Docker Development

When running via Docker Compose, the default fallback URL `http://localhost:8000` will be used automatically.

### Production Deployment

For GitHub Actions deployment, the `.env` file is automatically created during the CI/CD process with the production API URL.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Development Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:

   ```bash
   npm run dev
   ```

## Docker Setup

To run the entire application stack with Docker:

```bash
# From the project root
docker-compose up -d --build
```

The frontend will be available at `http://localhost:5173`
