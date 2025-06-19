import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Amazon Settings
    amazon_associate_tag: str = os.getenv("AMAZON_ASSOCIATE_TAG", "")
    amazon_access_key: str = os.getenv("AMAZON_ACCESS_KEY", "")
    amazon_secret_key: str = os.getenv("AMAZON_SECRET_KEY", "")

    # Flipkart Settings
    flipkart_affiliate_id: str = os.getenv("FLIPKART_AFFILIATE_ID", "")
    flipkart_affiliate_token: str = os.getenv("FLIPKART_AFFILIATE_TOKEN", "")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///affiliate_data.db")

    # Social Media
    twitter_api_key: str = os.getenv("TWITTER_API_KEY", "")
    twitter_api_secret: str = os.getenv("TWITTER_API_SECRET", "")
    twitter_access_token: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    twitter_access_token_secret: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # General Settings
    log_level: str = "INFO"
    base_path: Path = Path(__file__).parent.parent

    class Config:
        """Configuration class for env settings."""

        env_file = ".env"


settings = Settings()
