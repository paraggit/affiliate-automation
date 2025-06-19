import time
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from bs4 import BeautifulSoup

from ...core.base_affiliate import BaseAffiliateProvider, Product
from ...utils.logger import get_logger

logger = get_logger(__name__)


class AmazonAffiliate(BaseAffiliateProvider):
    """Amazon affiliate provider implementation."""

    BASE_URL = "https://www.amazon.com"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.associate_tag = config.get("amazon_associate_tag")
        self.validate_config()

    def get_required_config_fields(self) -> List[str]:
        return ["amazon_associate_tag"]

    def search_products(self, query: str, max_results: int = 10, **kwargs) -> List[Product]:
        """Search Amazon products."""
        products = []
        try:
            # Note: In production, you'd use Amazon Product Advertising API
            # This is a simplified example
            search_url = f"{self.BASE_URL}/s?k={query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            response = requests.get(search_url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse search results (simplified)
            items = soup.find_all('div', {'data-component-type': 's-search-result'})[:max_results]

            for item in items:
                try:
                    product = self._parse_search_item(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.error(f"Error parsing product: {e}")

        except Exception as e:
            logger.error(f"Error searching Amazon products: {e}")

        return products

    def _parse_search_item(self, item) -> Optional[Product]:
        """Parse individual search result item."""
        try:
            # Extract product details (simplified example)
            title_elem = item.find('h2', class_='s-size-mini-headline')
            if not title_elem:
                return None

            title = title_elem.text.strip()

            # Extract ASIN
            asin = item.get('data-asin', '')

            # Extract price
            price_elem = item.find('span', class_='a-price-whole')
            price = float(price_elem.text.replace(',', '').replace('.', '')) if price_elem else 0.0

            # Extract URL
            link_elem = item.find('a', class_='a-link-normal')
            url = f"{self.BASE_URL}{link_elem.get('href', '')}" if link_elem else ""

            # Generate affiliate URL
            affiliate_url = self.generate_affiliate_link(url)

            # Extract image
            img_elem = item.find('img', class_='s-image')
            image_url = img_elem.get('src', '') if img_elem else ""

            # Extract rating
            rating_elem = item.find('span', class_='a-icon-alt')
            rating = float(rating_elem.text.split()[0]) if rating_elem else None

            return Product(
                id=asin,
                title=title,
                price=price,
                url=url,
                affiliate_url=affiliate_url,
                image_url=image_url,
                rating=rating,
                platform="Amazon",
            )

        except Exception as e:
            logger.error(f"Error parsing search item: {e}")
            return None

    def get_product_details(self, product_id: str) -> Optional[Product]:
        """Get detailed product information."""
        try:
            product_url = f"{self.BASE_URL}/dp/{product_id}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

            response = requests.get(product_url, headers=headers, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Parse product details (simplified)
            title = soup.find('span', id='productTitle')
            title = title.text.strip() if title else ""

            # Price
            price_elem = soup.find('span', class_='a-price-whole')
            price = float(price_elem.text.replace(',', '').replace('.', '')) if price_elem else 0.0

            # Description
            feature_bullets = soup.find('div', id='feature-bullets')
            description = ""
            if feature_bullets:
                bullets = feature_bullets.find_all('span', class_='a-list-item')
                description = "\n".join([b.text.strip() for b in bullets if b.text.strip()])

            # Image
            img_elem = soup.find('img', id='landingImage')
            image_url = img_elem.get('src', '') if img_elem else ""

            # Rating
            rating_elem = soup.find('span', class_='a-icon-alt')
            rating = float(rating_elem.text.split()[0]) if rating_elem else None

            affiliate_url = self.generate_affiliate_link(product_url)

            return Product(
                id=product_id,
                title=title,
                price=price,
                url=product_url,
                affiliate_url=affiliate_url,
                image_url=image_url,
                rating=rating,
                description=description,
                platform="Amazon",
            )

        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None

    def generate_affiliate_link(self, product_url: str) -> str:
        """Generate Amazon affiliate link."""
        if not product_url or not self.associate_tag:
            return product_url

        # Parse URL
        parsed = urlparse(product_url)
        params = parse_qs(parsed.query)

        # Add affiliate tag
        params['tag'] = [self.associate_tag]

        # Rebuild URL
        new_query = urlencode(params, doseq=True)
        affiliate_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"

        return affiliate_url

    def get_trending_products(self, category: Optional[str] = None) -> List[Product]:
        """Get trending products from Amazon."""
        # In production, use Amazon's best sellers API
        query = f"best sellers {category}" if category else "best sellers"
        return self.search_products(query, max_results=20)
