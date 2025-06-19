from unittest.mock import Mock, patch

import pytest

from src.core.base_affiliate import Product
from src.platforms.amazon.amazon_affiliate import AmazonAffiliate


class TestAmazonAffiliate:
    @pytest.fixture
    def amazon_affiliate(self):
        config = {"amazon_associate_tag": "test-tag-20"}
        return AmazonAffiliate(config)

    def test_generate_affiliate_link(self, amazon_affiliate):
        """Test affiliate link generation."""
        url = "https://www.amazon.com/dp/B08N5WRWNW"
        affiliate_url = amazon_affiliate.generate_affiliate_link(url)

        assert "tag=test-tag-20" in affiliate_url
        assert "amazon.com" in affiliate_url

    @patch('requests.get')
    def test_search_products(self, mock_get, amazon_affiliate):
        """Test product search."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html>Mock Amazon search results</html>'
        mock_get.return_value = mock_response

        products = amazon_affiliate.search_products("laptop")

        assert isinstance(products, list)
        mock_get.assert_called_once()

    def test_validate_config(self, amazon_affiliate):
        """Test config validation."""
        assert amazon_affiliate.validate_config()

    def test_missing_config(self):
        """Test missing configuration."""
        with pytest.raises(ValueError):
            AmazonAffiliate({})
