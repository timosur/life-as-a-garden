# Deployment Guide

## Automatisches Deployment via GitHub Actions

Das Repository ist für automatisches Deployment mit GitHub Actions konfiguriert.

### Services Routing

- `https://garden.timosur.com/` → Frontend
- `https://garden.timosur.com/api/` → Backend
- `https://garden.timosur.com/rmapi/` → rmapi-wrapper

### Erstmaliges Setup

1. **Server vorbereiten:**

   ```bash
   # Domain DNS auf Server IP zeigen lassen
   # Port 80 und 443 in Firewall öffnen
   ```

2. **GitHub Secrets konfigurieren:**
   Die folgenden Secrets müssen in den GitHub Repository Settings konfiguriert werden:

   - `OPENAI_API_KEY`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`

3. **Self-hosted Runner einrichten:**
   Auf dem Zielserver einen GitHub Actions Self-hosted Runner einrichten.

4. **Automatisches Deployment:**
   Bei jedem Push auf den `main` Branch wird automatisch deployed:
   - SSL-Zertifikate werden beim ersten Deployment automatisch initialisiert
   - Services werden gebaut und gestartet
   - Bei nachfolgenden Deployments werden existierende Zertifikate wiederverwendet

### Manuelles Deployment

Falls du manuell deployen möchtest:

1. **Repository clonen:**

   ```bash
   git clone <repository-url>
   cd life-as-a-garden
   ```

2. **Environment Files erstellen:**

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

3. **SSL-Zertifikate initialisieren (nur beim ersten Mal):**

   ```bash
   chmod +x init-letsencrypt.sh
   ./init-letsencrypt.sh
   ```

4. **Services starten:**

   ```bash
   docker-compose up -d --build
   ```

### Updates deployen:

```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Logs anschauen:

```bash
# Alle Services
docker-compose logs -f

# Spezifische Services
docker-compose logs -f nginx
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f rmapi-wrapper
```

### SSL-Zertifikat erneuern:

Das Zertifikat wird automatisch alle 12 Stunden durch den certbot Container überprüft und erneuert.

Manuell erneuern:

```bash
docker-compose exec certbot certbot renew
docker-compose exec nginx nginx -s reload
```

## Lokale Entwicklung

Für die lokale Entwicklung kannst du die Services direkt starten, ohne Docker Compose zu verwenden.

Falls du doch Docker Compose lokal nutzen möchtest, verwende die `nginx.dev.conf` für HTTP ohne SSL:

```bash
# In docker-compose.yml die nginx volumes anpassen:
volumes:
  - ./nginx/nginx.dev.conf:/etc/nginx/nginx.conf
  - ./certbot/conf:/etc/letsencrypt
  - ./certbot/www:/var/www/certbot
```
