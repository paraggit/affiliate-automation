from datetime import datetime
from typing import Any, Dict, List, Optional

from ..platforms.amazon.amazon_affiliate import AmazonAffiliate
from ..platforms.flipkart.flipkart_affiliate import FlipkartAffiliate
from ..utils.database import Database
from ..utils.logger import get_logger
from .base_affiliate import BaseAffiliateProvider, Product

logger = get_logger(__name__)


class ProductManager:
    """Manages products across multiple affiliate platforms."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[str, BaseAffiliateProvider] = {}
        self.db = Database(config.get("database_url"))
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize available affiliate providers."""
        # Amazon
        if self.config.get("amazon_associate_tag"):
            self.providers["amazon"] = AmazonAffiliate(
                {
                    "amazon_associate_tag": self.config["amazon_associate_tag"],
                    "amazon_access_key": self.config.get("amazon_access_key"),
                    "amazon_secret_key": self.config.get("amazon_secret_key"),
                }
            )
            logger.info("Amazon affiliate provider initialized")

        # Flipkart
        if self.config.get("flipkart_affiliate_id"):
            self.providers["flipkart"] = FlipkartAffiliate(
                {
                    "flipkart_affiliate_id": self.config["flipkart_affiliate_id"],
                    "flipkart_affiliate_token": self.config["flipkart_affiliate_token"],
                }
            )
            logger.info("Flipkart affiliate provider initialized")

    def search_all_platforms(
        self, query: str, max_per_platform: int = 5
    ) -> Dict[str, List[Product]]:
        """Search products across all platforms."""
        results = {}

        for platform_name, provider in self.providers.items():
            try:
                products = provider.search_products(query, max_results=max_per_platform)
                results[platform_name] = products
                logger.info(f"Found {len(products)} products on {platform_name}")
            except Exception as e:
                logger.error(f"Error searching {platform_name}: {e}")
                results[platform_name] = []

        return results

    def get_best_deals(
        self, category: Optional[str] = None, min_discount: float = 10.0
    ) -> List[Product]:
        """Get best deals across all platforms."""
        all_deals = []

        for platform_name, provider in self.providers.items():
            try:
                products = provider.get_trending_products(category)
                # Filter by discount
                deals = [
                    p
                    for p in products
                    if p.discount_percentage and p.discount_percentage >= min_discount
                ]
                all_deals.extend(deals)
            except Exception as e:
                logger.error(f"Error getting deals from {platform_name}: {e}")

        # Sort by discount percentage
        all_deals.sort(key=lambda x: x.discount_percentage or 0, reverse=True)

        return all_deals

    def compare_prices(self, product_name: str) -> Dict[str, Product]:
        """Compare prices for similar products across platforms."""
        comparison = {}

        for platform_name, provider in self.providers.items():
            try:
                products = provider.search_products(product_name, max_results=1)
                if products:
                    comparison[platform_name] = products[0]
            except Exception as e:
                logger.error(f"Error comparing prices on {platform_name}: {e}")

        return comparison

    def save_product(self, product: Product):
        """Save product to database."""
        self.db.save_product(product)

    def get_saved_products(self, platform: Optional[str] = None) -> List[Product]:
        """Get saved products from database."""
        return self.db.get_products(platform)
