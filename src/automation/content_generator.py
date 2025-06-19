from typing import Any, Dict, List, Optional

import openai

from ..core.base_affiliate import Product
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ContentGenerator:
    """Generate content for affiliate products."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def generate_product_description(self, product: Product) -> str:
        """Generate engaging product description."""
        try:
            prompt = f"""
            Create an engaging product description for:
            Title: {product.title}
            Price: ${product.price}
            Original Price: ${product.original_price or product.price}
            Platform: {product.platform}

            Make it compelling and highlight key benefits. Keep it under 150 words.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled copywriter for affiliate marketing.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating product description: {e}")
            return product.description or product.title

    def generate_social_media_post(self, product: Product, platform: str = "twitter") -> str:
        """Generate social media post for product."""
        try:
            char_limits = {"twitter": 280, "instagram": 2200, "facebook": 63206}

            limit = char_limits.get(platform, 280)

            prompt = f"""
            Create a {platform} post for this product:
            Title: {product.title}
            Price: ${product.price}
            Discount: {product.discount_percentage}% off

            Include relevant hashtags and make it engaging.
            Character limit: {limit}
            Include the affiliate link at the end.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a social media expert specializing in {platform}.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                temperature=0.8,
            )

            post = response.choices[0].message.content.strip()

            # Add affiliate link
            if len(post) + len(product.affiliate_url) + 2 <= limit:
                post += f"\n{product.affiliate_url}"

            return post

        except Exception as e:
            logger.error(f"Error generating social media post: {e}")
            return f"Check out this amazing deal! {product.title} - Now ${product.price} {product.affiliate_url}"

    def generate_comparison_content(self, products: List[Product]) -> str:
        """Generate comparison content for multiple products."""
        try:
            product_list = "\n".join(
                [f"- {p.title} (${p.price}) from {p.platform}" for p in products[:5]]
            )

            prompt = f"""
            Create a product comparison article for these products:
            {product_list}

            Include pros/cons, price comparison, and recommendations.
            Make it informative and unbiased.
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert product reviewer."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating comparison content: {e}")
            return "Product comparison unavailable."
