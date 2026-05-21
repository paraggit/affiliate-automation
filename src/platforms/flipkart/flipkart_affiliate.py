from typing import Any, Dict, List, Optional

import requests

from ...core.base_affiliate import BaseAffiliateProvider, Product
from ...utils.logger import get_logger
from ...utils.retry import retry_on_failure

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

    @retry_on_failure(max_retries=3, exceptions=(requests.RequestException,))
    def _api_get(self, url: str, params: Optional[Dict] = None) -> Dict:
        """Make an API GET request with retry logic."""
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def search_products(self, query: str, max_results: int = 10, **kwargs) -> List[Product]:
        """Search Flipkart products."""
        products = []
        try:
            url = f"{self.BASE_URL}/search/json"
            params = {"query": query, "resultCount": max_results}

            data = self._api_get(url, params=params)
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

            selling_price = float(
                product_info.get("flipkartSellingPrice", {}).get("amount", 0)
            )
            original_price = float(
                product_info.get("maximumRetailPrice", {}).get("amount", 0)
            )
            discount = (
                round((original_price - selling_price) / original_price * 100, 1)
                if original_price > 0
                else None
            )

            return Product(
                id=product_info.get("productId", ""),
                title=product_info.get("title", ""),
                price=selling_price,
                original_price=original_price,
                discount_percentage=discount,
                url=product_info.get("productUrl", ""),
                affiliate_url=product_info.get("productUrl", ""),
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
            data = self._api_get(url)
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
            data = self._api_get(url)
            return self._parse_offers(data)
        except Exception as e:
            logger.error(f"Error getting Flipkart trending products: {e}")
            return []

    def _parse_offers(self, data: Dict[str, Any]) -> List[Product]:
        """Parse Flipkart offers/deals data."""
        products = []
        offers_list = data.get("topOffersList", [])
        for offer in offers_list:
            product = self._parse_product(offer)
            if product:
                products.append(product)
        return products
