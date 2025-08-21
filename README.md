# Life as a Garden (LaaG)

Ein automatisiertes System zur Pflege und Überwachung deines Gartens mit KI-gestützter Bildanalyse und intelligenten Benachrichtigungen.

## 🌱 Features

- **KI-Bildanalyse**: Automatische Erkennung von bewässerungsbedürftigen Pflanzen
- **Automatische Bewässerung**: Intelligente Bewässerungslogik basierend auf Pflanzentyp und -zustand
- **PDF-Generierung**: Automatische Erstellung von Garten-Statusberichten
- **reMarkable Integration**: Upload der Berichte zu deinem reMarkable Tablet
- **E-Mail Benachrichtigungen**: Automatische Benachrichtigungen bei erfolgreichen Analysen und Systemfehlern
- **Health Monitoring**: Umfassende Systemüberwachung mit Frühwarnsystem
- **Web-Dashboard**: React-basierte Benutzeroberfläche zur Gartenverwaltung

## 📧 E-Mail Benachrichtigungen

Das System sendet automatisch E-Mail-Benachrichtigungen für:

- ✅ **Erfolgreiche nächtliche Analysen** mit Garten-Statistiken
- ⚠️ **Health Check Fehler** mit detaillierter Fehlerdiagnose
- 💧 **Bewässerungs-Updates** nach automatischen Zyklen

## 🚀 Quick Start

1. **Repository klonen**:

   ```bash
   git clone https://github.com/timosur/life-as-a-garden.git
   cd life-as-a-garden
   ```

2. **Umgebungsvariablen konfigurieren**:

   ```bash
   cp backend/.env.example backend/.env
   # Bearbeite backend/.env mit deinen API-Schlüsseln und E-Mail-Einstellungen

   cp .env.example .env
   # Bearbeite .env mit deinen Basic Auth Zugangsdaten
   ```

3. **Basic Authentication einrichten**:

   ```bash
   # Setze sichere Zugangsdaten in .env
   AUTH_USER=your-username
   AUTH_PASS=your-secure-password
   ```

4. **System starten**:

   ```bash
   docker-compose up -d --build
   ```

5. **E-Mail-Konfiguration testen**:

   ```bash
   curl -X POST http://localhost:8000/api/notifications/test-email
   ```

## 🔧 Konfiguration

Siehe [E-Mail Benachrichtigungen](backend/EMAIL_NOTIFICATIONS.md) für detaillierte Konfigurationsanleitungen.

Für GitHub Deployment siehe [GitHub Secrets](/.github/SECRETS.md).

## 📱 Automatischer Zeitplan

- **Täglich 01:00 Uhr**: Automatische Analyse und Bewässerung
- **Kontinuierlich**: Health Check Überwachung mit E-Mail-Alerts

This is my life as a garden (LaaG)
