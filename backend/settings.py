from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    openai_api_key: str
    frontend_url: str = "http://localhost:5173/"
    rmapi_service_url: str = "http://localhost:8001"

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
