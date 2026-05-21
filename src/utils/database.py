from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..core.base_affiliate import Product


class Base(DeclarativeBase):
    pass


class ProductModel(Base):
    __tablename__ = 'products'

    id = Column(String, primary_key=True)
    platform = Column(String, primary_key=True)
    title = Column(String)
    price = Column(Float)
    original_price = Column(Float)
    discount_percentage = Column(Float)
    url = Column(Text)
    affiliate_url = Column(Text)
    image_url = Column(Text)
    rating = Column(Float)
    review_count = Column(Integer)
    category = Column(String)
    description = Column(Text)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_product(self) -> Product:
        return Product(
            id=self.id,
            title=self.title,
            price=self.price,
            original_price=self.original_price,
            discount_percentage=self.discount_percentage,
            url=self.url,
            affiliate_url=self.affiliate_url,
            image_url=self.image_url,
            rating=self.rating,
            review_count=self.review_count,
            category=self.category,
            description=self.description,
            platform=self.platform,
            last_updated=self.last_updated,
        )


class Database:
    """Database handler for product storage and retrieval."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def save_product(self, product: Product):
        """Save or update product in database."""
        with self.SessionLocal() as session:
            existing = (
                session.query(ProductModel)
                .filter_by(id=product.id, platform=product.platform)
                .first()
            )

            if existing:
                existing.title = product.title
                existing.price = product.price
                existing.original_price = product.original_price
                existing.discount_percentage = product.discount_percentage
                existing.url = product.url
                existing.affiliate_url = product.affiliate_url
                existing.image_url = product.image_url
                existing.rating = product.rating
                existing.review_count = product.review_count
                existing.category = product.category
                existing.description = product.description
                existing.last_updated = datetime.now(timezone.utc)
            else:
                new_product = ProductModel(
                    id=product.id,
                    platform=product.platform,
                    title=product.title,
                    price=product.price,
                    original_price=product.original_price,
                    discount_percentage=product.discount_percentage,
                    url=product.url,
                    affiliate_url=product.affiliate_url,
                    image_url=product.image_url,
                    rating=product.rating,
                    review_count=product.review_count,
                    category=product.category,
                    description=product.description,
                )
                session.add(new_product)

            session.commit()

    def get_products(self, platform: Optional[str] = None) -> List[Product]:
        """Get products from database."""
        with self.SessionLocal() as session:
            query = session.query(ProductModel)
            if platform:
                query = query.filter_by(platform=platform)

            return [p.to_product() for p in query.all()]

    def get_product(self, product_id: str, platform: str) -> Optional[Product]:
        """Get single product from database."""
        with self.SessionLocal() as session:
            product_model = (
                session.query(ProductModel).filter_by(id=product_id, platform=platform).first()
            )

            return product_model.to_product() if product_model else None
