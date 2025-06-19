from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Product:
    """Universal product model for all platforms."""

    id: str
    title: str
    price: float
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    url: str = ""
    affiliate_url: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    platform: str = ""
    last_updated: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "original_price": self.original_price,
            "discount_percentage": self.discount_percentage,
            "url": self.url,
            "affiliate_url": self.affiliate_url,
            "image_url": self.image_url,
            "rating": self.rating,
            "review_count": self.review_count,
            "category": self.category,
            "description": self.description,
            "platform": self.platform,
            "last_updated": self.last_updated.isoformat(),
        }


class BaseAffiliateProvider(ABC):
    """Abstract base class for affiliate providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.platform_name = self.__class__.__name__.replace("Affiliate", "")

    @abstractmethod
    def search_products(self, query: str, **kwargs) -> List[Product]:
        """Search for products on the platform."""
        pass

    @abstractmethod
    def get_product_details(self, product_id: str) -> Optional[Product]:
        """Get detailed information about a specific product."""
        pass

    @abstractmethod
    def generate_affiliate_link(self, product_url: str) -> str:
        """Generate affiliate link for a product."""
        pass

    @abstractmethod
    def get_trending_products(self, category: Optional[str] = None) -> List[Product]:
        """Get trending/popular products."""
        pass

    def validate_config(self) -> bool:
        """Validate required configuration."""
        required_fields = self.get_required_config_fields()
        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Missing required config field: {field}")
        return True

    @abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """Return list of required configuration fields."""
        pass
