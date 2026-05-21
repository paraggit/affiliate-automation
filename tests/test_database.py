import pytest

from src.core.base_affiliate import Product
from src.utils.database import Database


class TestDatabase:
    @pytest.fixture
    def db(self, tmp_path):
        db_path = tmp_path / "test.db"
        return Database(f"sqlite:///{db_path}")

    @pytest.fixture
    def sample_product(self):
        return Product(
            id="TEST123",
            title="Test Product",
            price=29.99,
            original_price=49.99,
            discount_percentage=40.0,
            url="https://example.com/product/TEST123",
            affiliate_url="https://example.com/product/TEST123?tag=test",
            image_url="https://example.com/image.jpg",
            rating=4.5,
            review_count=100,
            category="Electronics",
            description="A test product",
            platform="Amazon",
        )

    def test_save_and_get_product(self, db, sample_product):
        db.save_product(sample_product)

        result = db.get_product("TEST123", "Amazon")
        assert result is not None
        assert result.id == "TEST123"
        assert result.title == "Test Product"
        assert result.price == 29.99
        assert result.platform == "Amazon"

    def test_save_product_update(self, db, sample_product):
        db.save_product(sample_product)

        sample_product.price = 19.99
        sample_product.title = "Updated Product"
        db.save_product(sample_product)

        result = db.get_product("TEST123", "Amazon")
        assert result.price == 19.99
        assert result.title == "Updated Product"

    def test_get_products_all(self, db, sample_product):
        db.save_product(sample_product)

        flipkart_product = Product(
            id="FK456",
            title="Flipkart Product",
            price=39.99,
            platform="Flipkart",
        )
        db.save_product(flipkart_product)

        products = db.get_products()
        assert len(products) == 2

    def test_get_products_by_platform(self, db, sample_product):
        db.save_product(sample_product)

        flipkart_product = Product(
            id="FK456",
            title="Flipkart Product",
            price=39.99,
            platform="Flipkart",
        )
        db.save_product(flipkart_product)

        amazon_products = db.get_products(platform="Amazon")
        assert len(amazon_products) == 1
        assert amazon_products[0].platform == "Amazon"

    def test_get_nonexistent_product(self, db):
        result = db.get_product("NONEXISTENT", "Amazon")
        assert result is None

    def test_get_products_empty_db(self, db):
        products = db.get_products()
        assert products == []
