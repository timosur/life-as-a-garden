# Life as a Garden (LaaG)

An automated system for maintaining and monitoring your garden with AI-powered image analysis and smart notifications.

## 🌱 Features

- **AI Image Analysis**: Automatic detection of plants needing watering
- **Automatic Watering**: Intelligent watering logic based on plant type and condition
- **PDF Generation**: Automatic creation of garden status reports
- **reMarkable Integration**: Upload reports to your reMarkable tablet
- **Email Notifications**: Automatic notifications for successful analyses and system errors
- **Health Monitoring**: Comprehensive system monitoring with early warning system
- **Web Dashboard**: React-based user interface for garden management

## 📧 Email Notifications

The system automatically sends email notifications for:

- ✅ **Successful nightly analyses** with garden statistics
- ⚠️ **Health check errors** with detailed error diagnostics
- 💧 **Watering updates** after automatic cycles

## 🚀 Quick Start

1. **Clone the repository**:

   ```bash
   git clone https://github.com/timosur/life-as-a-garden.git
   cd life-as-a-garden
   ```

2. **Configure environment variables**:

   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys and email settings

   cp .env.example .env
   # Edit .env with your basic auth credentials
   ```

3. **Set up basic authentication**:

   ```bash
   # Set secure credentials in .env
   AUTH_USER=your-username
   AUTH_PASS=your-secure-password
   ```

4. **Start the system**:

   ```bash
   docker-compose up -d --build
   ```

5. **Test email configuration**:

   ```bash
   curl -X POST http://localhost:8000/api/notifications/test-email
   ```

## 🔧 Configuration

See [Email Notifications](backend/EMAIL_NOTIFICATIONS.md) for detailed configuration instructions.

For GitHub deployment, see [GitHub Secrets](/.github/SECRETS.md).

## 📱 Automatic Schedule

- **Daily at 01:00**: Automatic analysis and watering
- **Continuous**: Health check monitoring with email alerts

This is my life as a garden (LaaG)
