import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import schedule
import tweepy

from ..core.base_affiliate import Product
from ..utils.logger import get_logger
from .content_generator import ContentGenerator

logger = get_logger(__name__)


class SocialMediaPoster:
    """Automate social media posting for affiliate products."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.content_generator = ContentGenerator(config.get("openai_api_key"))
        self._setup_twitter()

    def _setup_twitter(self):
        """Setup Twitter API client."""
        try:
            auth = tweepy.OAuthHandler(
                self.config.get("twitter_api_key"), self.config.get("twitter_api_secret")
            )
            auth.set_access_token(
                self.config.get("twitter_access_token"),
                self.config.get("twitter_access_token_secret"),
            )
            self.twitter_api = tweepy.API(auth)
            logger.info("Twitter API initialized")
        except Exception as e:
            logger.error(f"Error setting up Twitter: {e}")
            self.twitter_api = None

    def post_to_twitter(self, content: str, image_url: Optional[str] = None) -> bool:
        """Post content to Twitter."""
        if not self.twitter_api:
            logger.error("Twitter API not initialized")
            return False

        try:
            if image_url:
                # Download and upload image
                # For production, implement proper image handling
                self.twitter_api.update_status(content)
            else:
                self.twitter_api.update_status(content)

            logger.info("Successfully posted to Twitter")
            return True

        except Exception as e:
            logger.error(f"Error posting to Twitter: {e}")
            return False

    def schedule_product_posts(self, products: List[Product], posts_per_day: int = 3):
        """Schedule automatic posting of products."""
        post_times = ["09:00", "14:00", "19:00"][:posts_per_day]

        def post_product():
            if products:
                product = products.pop(0)
                content = self.content_generator.generate_social_media_post(product, "twitter")
                self.post_to_twitter(content, product.image_url)

        for time_str in post_times:
            schedule.every().day.at(time_str).do(post_product)

        logger.info(f"Scheduled {posts_per_day} posts per day")

    def run_scheduler(self):
        """Run the scheduled posts."""
        logger.info("Starting social media scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
