from unittest.mock import MagicMock, patch

import pytest

from src.core.base_affiliate import Product
from src.core.product_manager import ProductManager


class TestProductManager:
    @pytest.fixture
    def manager(self, tmp_path):
        db_path = tmp_path / "test.db"
        config = {
            "database_url": f"sqlite:///{db_path}",
            "amazon_associate_tag": "test-tag-20",
            "flipkart_affiliate_id": "",
            "flipkart_affiliate_token": "",
        }
        with patch(
            'src.core.product_manager.AmazonAffiliate'
        ) as MockAmazon:
            mock_amazon = MockAmazon.return_value
            mock_amazon.search_products.return_value = []
            mock_amazon.get_trending_products.return_value = []

            mgr = ProductManager(config)
            mgr.providers["amazon"] = mock_amazon
            return mgr

    @pytest.fixture
    def sample_products(self):
        return [
            Product(
                id="A1",
                title="Product A",
                price=29.99,
                discount_percentage=30.0,
                platform="Amazon",
            ),
            Product(
                id="A2",
                title="Product B",
                price=49.99,
                discount_percentage=15.0,
                platform="Amazon",
            ),
        ]

    def test_search_all_platforms(self, manager, sample_products):
        manager.providers["amazon"].search_products.return_value = sample_products

        results = manager.search_all_platforms("laptop")
        assert "amazon" in results
        assert len(results["amazon"]) == 2

    def test_search_all_platforms_error_handling(self, manager):
        manager.providers["amazon"].search_products.side_effect = Exception("Network error")

        results = manager.search_all_platforms("laptop")
        assert results["amazon"] == []

    def test_get_best_deals(self, manager, sample_products):
        manager.providers["amazon"].get_trending_products.return_value = sample_products

        deals = manager.get_best_deals(min_discount=20.0)
        assert len(deals) == 1
        assert deals[0].id == "A1"

    def test_get_best_deals_sorted_by_discount(self, manager):
        products = [
            Product(id="1", title="P1", price=10, discount_percentage=20.0, platform="Amazon"),
            Product(id="2", title="P2", price=10, discount_percentage=50.0, platform="Amazon"),
            Product(id="3", title="P3", price=10, discount_percentage=35.0, platform="Amazon"),
        ]
        manager.providers["amazon"].get_trending_products.return_value = products

        deals = manager.get_best_deals(min_discount=10.0)
        assert [d.discount_percentage for d in deals] == [50.0, 35.0, 20.0]

    def test_compare_prices(self, manager, sample_products):
        manager.providers["amazon"].search_products.return_value = [sample_products[0]]

        comparison = manager.compare_prices("laptop")
        assert "amazon" in comparison
        assert comparison["amazon"].id == "A1"

    def test_compare_prices_no_results(self, manager):
        manager.providers["amazon"].search_products.return_value = []

        comparison = manager.compare_prices("nonexistent")
        assert "amazon" not in comparison

    def test_save_and_get_products(self, manager):
        product = Product(
            id="TEST1",
            title="Test Product",
            price=19.99,
            platform="Amazon",
        )

        manager.save_product(product)
        saved = manager.get_saved_products()
        assert len(saved) == 1
        assert saved[0].id == "TEST1"

    def test_get_saved_products_by_platform(self, manager):
        p1 = Product(id="A1", title="Amazon Product", price=10, platform="Amazon")
        p2 = Product(id="F1", title="Flipkart Product", price=10, platform="Flipkart")

        manager.save_product(p1)
        manager.save_product(p2)

        amazon_only = manager.get_saved_products(platform="Amazon")
        assert len(amazon_only) == 1
        assert amazon_only[0].platform == "Amazon"
