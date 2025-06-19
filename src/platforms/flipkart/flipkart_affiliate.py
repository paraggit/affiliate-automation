from typing import Any, Dict, List, Optional

import requests

from ...core.base_affiliate import BaseAffiliateProvider, Product
from ...utils.logger import get_logger

logger = get_logger(__name__)


class FlipkartAffiliate(BaseAffiliateProvider):
    """Flipkart affiliate provider implementation."""

    BASE_URL = "https://affiliate-api.flipkart.net/affiliate"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.affiliate_id = config.get("flipkart_affiliate_id")
        self.affiliate_token = config.get("flipkart_affiliate_token")
        self.validate_config()

    def get_required_config_fields(self) -> List[str]:
        return ["flipkart_affiliate_id", "flipkart_affiliate_token"]

    def _get_headers(self) -> Dict[str, str]:
        return {"Fk-Affiliate-Id": self.affiliate_id, "Fk-Affiliate-Token": self.affiliate_token}

    def search_products(self, query: str, max_results: int = 10, **kwargs) -> List[Product]:
        """Search Flipkart products."""
        products = []
        try:
            url = f"{self.BASE_URL}/search/json"
            params = {"query": query, "resultCount": max_results}

            response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                products_data = data.get("products", [])

                for item in products_data:
                    product = self._parse_product(item)
                    if product:
                        products.append(product)

        except Exception as e:
            logger.error(f"Error searching Flipkart products: {e}")

        return products

    def _parse_product(self, data: Dict[str, Any]) -> Optional[Product]:
        """Parse Flipkart product data."""
        try:
            product_info = data.get("productBaseInfoV1", {})

            return Product(
                id=product_info.get("productId", ""),
                title=product_info.get("title", ""),
                price=float(product_info.get("flipkartSellingPrice", {}).get("amount", 0)),
                original_price=float(product_info.get("maximumRetailPrice", {}).get("amount", 0)),
                url=product_info.get("productUrl", ""),
                affiliate_url=product_info.get("productUrl", ""),  # Already contains affiliate ID
                image_url=product_info.get("imageUrls", {}).get("400x400", ""),
                category=product_info.get("categoryPath", ""),
                description=product_info.get("productDescription", ""),
                platform="Flipkart",
            )

        except Exception as e:
            logger.error(f"Error parsing Flipkart product: {e}")
            return None

    def get_product_details(self, product_id: str) -> Optional[Product]:
        """Get detailed product information from Flipkart."""
        try:
            url = f"{self.BASE_URL}/products/{product_id}"
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                data = response.json()
                return self._parse_product(data)

        except Exception as e:
            logger.error(f"Error getting Flipkart product details: {e}")

        return None

    def generate_affiliate_link(self, product_url: str) -> str:
        """Flipkart URLs already contain affiliate information when fetched via API."""
        return product_url

    def get_trending_products(self, category: Optional[str] = None) -> List[Product]:
        """Get trending products from Flipkart."""
        try:
            url = f"{self.BASE_URL}/offers/v1/top/json"
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                data = response.json()
                # Parse top offers data
                return self._parse_offers(data)

        except Exception as e:
            logger.error(f"Error getting Flipkart trending products: {e}")

        return []

    def _parse_offers(self, data: Dict[str, Any]) -> List[Product]:
        """Parse Flipkart offers/deals data."""
        products = []
        # Implementation would parse the offers response
        # This is a placeholder
        return products
