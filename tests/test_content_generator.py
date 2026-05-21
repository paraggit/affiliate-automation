from unittest.mock import MagicMock, patch

import pytest

from src.automation.content_generator import ContentGenerator
from src.core.base_affiliate import Product


class TestContentGenerator:
    @pytest.fixture
    def generator(self):
        with patch('src.automation.content_generator.OpenAI'):
            return ContentGenerator(api_key="test-key", model="gpt-4o-mini")

    @pytest.fixture
    def sample_product(self):
        return Product(
            id="TEST123",
            title="Wireless Headphones",
            price=49.99,
            original_price=79.99,
            discount_percentage=37.5,
            affiliate_url="https://example.com/product?tag=test",
            platform="Amazon",
            description="Great wireless headphones",
        )

    def test_generate_product_description(self, generator, sample_product):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Amazing wireless headphones at a great price!"
        generator.client.chat.completions.create.return_value = mock_response

        result = generator.generate_product_description(sample_product)
        assert result == "Amazing wireless headphones at a great price!"
        generator.client.chat.completions.create.assert_called_once()

    def test_generate_product_description_fallback(self, generator, sample_product):
        generator.client.chat.completions.create.side_effect = Exception("API error")

        result = generator.generate_product_description(sample_product)
        assert result == sample_product.description

    def test_generate_product_description_fallback_no_description(self, generator):
        product = Product(id="1", title="Test Product", price=10.0, platform="Amazon")
        generator.client.chat.completions.create.side_effect = Exception("API error")

        result = generator.generate_product_description(product)
        assert result == "Test Product"

    def test_generate_social_media_post(self, generator, sample_product):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Check out these headphones! #deals"
        generator.client.chat.completions.create.return_value = mock_response

        result = generator.generate_social_media_post(sample_product, "twitter")
        assert "Check out these headphones!" in result

    def test_generate_social_media_post_appends_link(self, generator, sample_product):
        short_post = "Buy now!"
        mock_response = MagicMock()
        mock_response.choices[0].message.content = short_post
        generator.client.chat.completions.create.return_value = mock_response

        result = generator.generate_social_media_post(sample_product, "twitter")
        assert sample_product.affiliate_url in result

    def test_generate_social_media_post_fallback(self, generator, sample_product):
        generator.client.chat.completions.create.side_effect = Exception("API error")

        result = generator.generate_social_media_post(sample_product, "twitter")
        assert sample_product.title in result
        assert str(sample_product.price) in result

    def test_generate_comparison_content(self, generator):
        products = [
            Product(id="1", title="Product A", price=10.0, platform="Amazon"),
            Product(id="2", title="Product B", price=20.0, platform="Flipkart"),
        ]

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Product A vs Product B comparison"
        generator.client.chat.completions.create.return_value = mock_response

        result = generator.generate_comparison_content(products)
        assert result == "Product A vs Product B comparison"

    def test_generate_comparison_content_fallback(self, generator):
        generator.client.chat.completions.create.side_effect = Exception("API error")

        result = generator.generate_comparison_content([])
        assert result == "Product comparison unavailable."
