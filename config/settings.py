from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Amazon Settings
    amazon_associate_tag: str = ""
    amazon_access_key: str = ""
    amazon_secret_key: str = ""

    # Flipkart Settings
    flipkart_affiliate_id: str = ""
    flipkart_affiliate_token: str = ""

    # Database
    database_url: str = "sqlite:///affiliate_data.db"

    # Social Media
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_token_secret: str = ""

    # OpenAI
    openai_api_key: str = ""

    # General Settings
    log_level: str = "INFO"
    base_path: Path = Path(__file__).parent.parent

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
