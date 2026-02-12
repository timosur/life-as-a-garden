from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    openai_api_key: str
    frontend_url: str = "http://localhost:5173"
    rmapi_service_url: str = "http://localhost:8001"

    # Database settings - individual vars for K8s, or set DATABASE_URL directly
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "garden"
    db_user: str = "garden"
    db_password: str = "garden"
    database_url: str = ""

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.database_url:
            self.database_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return self

    # Email settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    notification_email: str = "lebensgarten@timosur.com"
    email_notifications_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def frontend_base_url(self) -> str:
        """Get the frontend base URL, ensuring it ends with a slash."""
        url = self.frontend_url
        if not url.endswith("/"):
            url += "/"
        return url


# Global settings instance
settings = Settings()
