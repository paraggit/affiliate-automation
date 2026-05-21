from unittest.mock import Mock, patch

import pytest

from src.platforms.flipkart.flipkart_affiliate import FlipkartAffiliate


class TestFlipkartAffiliate:
    @pytest.fixture
    def flipkart(self):
        config = {
            "flipkart_affiliate_id": "test-id",
            "flipkart_affiliate_token": "test-token",
        }
        return FlipkartAffiliate(config)

    def test_validate_config(self, flipkart):
        assert flipkart.validate_config()

    def test_missing_config(self):
        with pytest.raises(ValueError):
            FlipkartAffiliate({})

    def test_missing_token(self):
        with pytest.raises(ValueError):
            FlipkartAffiliate({"flipkart_affiliate_id": "test-id"})

    def test_get_headers(self, flipkart):
        headers = flipkart._get_headers()
        assert headers["Fk-Affiliate-Id"] == "test-id"
        assert headers["Fk-Affiliate-Token"] == "test-token"

    def test_generate_affiliate_link(self, flipkart):
        url = "https://www.flipkart.com/product/123"
        assert flipkart.generate_affiliate_link(url) == url

    @patch('src.platforms.flipkart.flipkart_affiliate.FlipkartAffiliate._api_get')
    def test_search_products(self, mock_api_get, flipkart):
        mock_api_get.return_value = {
            "products": [
                {
                    "productBaseInfoV1": {
                        "productId": "FK123",
                        "title": "Test Product",
                        "flipkartSellingPrice": {"amount": 999},
                        "maximumRetailPrice": {"amount": 1499},
                        "productUrl": "https://flipkart.com/product/FK123",
                        "imageUrls": {"400x400": "https://img.flipkart.com/test.jpg"},
                        "categoryPath": "Electronics",
                        "productDescription": "A test product",
                    }
                }
            ]
        }

        products = flipkart.search_products("laptop")
        assert len(products) == 1
        assert products[0].id == "FK123"
        assert products[0].price == 999.0
        assert products[0].original_price == 1499.0
        assert products[0].platform == "Flipkart"

    @patch('src.platforms.flipkart.flipkart_affiliate.FlipkartAffiliate._api_get')
    def test_search_products_empty(self, mock_api_get, flipkart):
        mock_api_get.return_value = {"products": []}
        products = flipkart.search_products("nonexistent")
        assert products == []

    @patch('src.platforms.flipkart.flipkart_affiliate.FlipkartAffiliate._api_get')
    def test_get_product_details(self, mock_api_get, flipkart):
        mock_api_get.return_value = {
            "productBaseInfoV1": {
                "productId": "FK123",
                "title": "Test Product",
                "flipkartSellingPrice": {"amount": 999},
                "maximumRetailPrice": {"amount": 1499},
                "productUrl": "https://flipkart.com/product/FK123",
                "imageUrls": {},
                "categoryPath": "",
                "productDescription": "",
            }
        }

        product = flipkart.get_product_details("FK123")
        assert product is not None
        assert product.id == "FK123"

    def test_parse_product_discount_calculation(self, flipkart):
        data = {
            "productBaseInfoV1": {
                "productId": "FK123",
                "title": "Test",
                "flipkartSellingPrice": {"amount": 750},
                "maximumRetailPrice": {"amount": 1000},
                "productUrl": "",
                "imageUrls": {},
                "categoryPath": "",
                "productDescription": "",
            }
        }
        product = flipkart._parse_product(data)
        assert product.discount_percentage == 25.0

    @patch('src.platforms.flipkart.flipkart_affiliate.FlipkartAffiliate._api_get')
    def test_get_trending_products(self, mock_api_get, flipkart):
        mock_api_get.return_value = {"topOffersList": []}
        products = flipkart.get_trending_products()
        assert products == []
