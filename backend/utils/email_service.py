"""
Email notification service for Life as a Garden API

Provides email notifications for:
- Successful analysis runs
- Health check failures
- System alerts
"""

import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.notification_email = settings.notification_email
        self.enabled = settings.email_notifications_enabled

    def _send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """
        Send an email notification.

        Args:
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML formatted

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info("Email notifications are disabled")
            return False

        if not self.smtp_username or not self.smtp_password:
            logger.warning("Email credentials not configured, skipping notification")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = self.notification_email
            msg["Subject"] = subject

            # Attach body
            body_type = "html" if is_html else "plain"
            msg.attach(MIMEText(body, body_type))

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email notification sent successfully: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False

    def send_analysis_success_notification(
        self, analysis_result: Dict[str, Any], stats: Dict[str, Any]
    ) -> bool:
        """
        Send notification for successful analysis run.

        Args:
            analysis_result: Result from the analysis function
            stats: Garden statistics

        Returns:
            bool: True if notification was sent successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subject = f"🌱 Lebensgarten - Erfolgreiche Analyse ({timestamp})"

        # Extract key information from analysis result
        total_plants = stats.get("total_plants", "N/A")
        healthy_plants = stats.get("healthy_plants", "N/A")
        plants_needing_attention = stats.get("plants_needing_attention", "N/A")

        body = f"""
Hallo!

Die nächtliche Analyse des Lebensgartens wurde erfolgreich durchgeführt.

📊 Garten-Statistiken:
• Gesamte Pflanzen: {total_plants}
• Gesunde Pflanzen: {healthy_plants}
• Pflanzen benötigen Aufmerksamkeit: {plants_needing_attention}

⏰ Zeitpunkt: {timestamp}

Die Ergebnisse wurden verarbeitet und das PDF wurde zum reMarkable hochgeladen.

Beste Grüße,
Dein Lebensgarten System 🌿
        """

        return self._send_email(subject, body.strip())

    def send_health_check_failure_notification(
        self, health_status: Dict[str, Any]
    ) -> bool:
        """
        Send notification for health check failures.

        Args:
            health_status: Health check result with issues

        Returns:
            bool: True if notification was sent successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        subject = f"⚠️ Lebensgarten - Health Check Fehler ({timestamp})"

        # Extract failed services
        failed_services = []
        services = health_status.get("services", {})

        for service_name, service_status in services.items():
            if service_status.get("status") != "healthy":
                error = service_status.get("error", "Unbekannter Fehler")
                failed_services.append(f"• {service_name}: {error}")

        issues = health_status.get("issues", [])
        overall_status = health_status.get("overall_status", "unknown")

        body = f"""
Hallo!

Das Lebensgarten System hat Probleme festgestellt.

🚨 Gesamtstatus: {overall_status.upper()}

❌ Betroffene Services:
{chr(10).join(failed_services) if failed_services else "• Keine spezifischen Service-Fehler"}

📝 Gemeldete Probleme:
{chr(10).join([f"• {issue}" for issue in issues]) if issues else "• Keine spezifischen Probleme gemeldet"}

⏰ Zeitpunkt: {timestamp}

Bitte prüfe das System und behebe die Probleme.

Beste Grüße,
Dein Lebensgarten System 🌿
        """

        return self._send_email(subject, body.strip())

    def send_watering_notification(
        self, watering_result: Dict[str, Any], stats: Dict[str, Any]
    ) -> bool:
        """
        Send notification for watering operations.

        Args:
            watering_result: Result from watering operation
            stats: Garden statistics after watering

        Returns:
            bool: True if notification was sent successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        success = watering_result.get("success", False)
        plants_watered = watering_result.get("plants_watered", 0)

        if success:
            subject = f"💧 Lebensgarten - Bewässerung erfolgreich ({timestamp})"

            body = f"""
Hallo!

Die automatische Bewässerung wurde erfolgreich durchgeführt.

💧 Bewässerungs-Details:
• Pflanzen bewässert: {plants_watered}
• Gesamte Pflanzen: {stats.get("total_plants", "N/A")}

⏰ Zeitpunkt: {timestamp}

Alle durstigen Pflanzen wurden versorgt! 🌱

Beste Grüße,
Dein Lebensgarten System 🌿
            """
        else:
            subject = f"⚠️ Lebensgarten - Bewässerung fehlgeschlagen ({timestamp})"
            error = watering_result.get("error", "Unbekannter Fehler")

            body = f"""
Hallo!

Die automatische Bewässerung ist fehlgeschlagen.

❌ Fehler: {error}
⏰ Zeitpunkt: {timestamp}

Bitte prüfe das System und die Bewässerungsfunktion.

Beste Grüße,
Dein Lebensgarten System 🌿
            """

        return self._send_email(subject, body.strip())

    def test_email_configuration(self) -> Dict[str, Any]:
        """
        Test the email configuration by sending a test email.

        Returns:
            Dict with test result
        """
        if not self.enabled:
            return {"success": False, "message": "Email notifications are disabled"}

        if not self.smtp_username or not self.smtp_password:
            return {"success": False, "message": "Email credentials not configured"}

        subject = "🧪 Lebensgarten - Test E-Mail"
        body = f"""
Hallo!

Dies ist eine Test-E-Mail vom Lebensgarten System.

Wenn du diese E-Mail erhältst, funktioniert die E-Mail-Konfiguration korrekt.

⏰ Gesendet: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Beste Grüße,
Dein Lebensgarten System 🌿
        """

        success = self._send_email(subject, body.strip())

        return {
            "success": success,
            "message": "Test email sent successfully"
            if success
            else "Failed to send test email",
            "recipient": self.notification_email,
        }


# Global email service instance
email_service = EmailService()
