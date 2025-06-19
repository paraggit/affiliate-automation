#!/usr/bin/env python3
"""
Affiliate Marketing Automation System.

Main entry point for the application
"""

import argparse
import sys
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from config.settings import settings
from src.automation.content_generator import ContentGenerator
from src.automation.social_media_poster import SocialMediaPoster
from src.core.product_manager import ProductManager
from src.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


class AffiliateAutomation:
    def __init__(self):
        self.config = {
            "amazon_associate_tag": settings.amazon_associate_tag,
            "amazon_access_key": settings.amazon_access_key,
            "amazon_secret_key": settings.amazon_secret_key,
            "flipkart_affiliate_id": settings.flipkart_affiliate_id,
            "flipkart_affiliate_token": settings.flipkart_affiliate_token,
            "database_url": settings.database_url,
            "openai_api_key": settings.openai_api_key,
            "twitter_api_key": settings.twitter_api_key,
            "twitter_api_secret": settings.twitter_api_secret,
            "twitter_access_token": settings.twitter_access_token,
            "twitter_access_token_secret": settings.twitter_access_token_secret,
        }

        self.product_manager = ProductManager(self.config)
        self.content_generator = (
            ContentGenerator(settings.openai_api_key) if settings.openai_api_key else None
        )
        self.social_media_poster = (
            SocialMediaPoster(self.config) if settings.twitter_api_key else None
        )

    def search_products(self, query: str):
        """Search products across all platforms."""
        console.print(f"\n[bold cyan]Searching for:[/bold cyan] {query}")

        results = self.product_manager.search_all_platforms(query)

        for platform, products in results.items():
            if products:
                table = Table(title=f"{platform.capitalize()} Results")
                table.add_column("Title", style="cyan", no_wrap=False)
                table.add_column("Price", style="green")
                table.add_column("Rating", style="yellow")
                table.add_column("Link", style="blue", no_wrap=True)

                for product in products[:5]:  # Show top 5
                    table.add_row(
                        product.title[:50] + "..." if len(product.title) > 50 else product.title,
                        f"${product.price:.2f}",
                        f"{product.rating or 'N/A'}",
                        product.affiliate_url[:30] + "...",
                    )

                console.print(table)
            else:
                console.print(f"[yellow]No results found on {platform}[/yellow]")

    def compare_prices(self, product_name: str):
        """Compare prices across platforms."""
        console.print(f"\n[bold cyan]Comparing prices for:[/bold cyan] {product_name}")

        comparison = self.product_manager.compare_prices(product_name)

        if comparison:
            table = Table(title="Price Comparison")
            table.add_column("Platform", style="cyan")
            table.add_column("Product", style="white", no_wrap=False)
            table.add_column("Price", style="green")
            table.add_column("Link", style="blue")

            for platform, product in comparison.items():
                table.add_row(
                    platform.capitalize(),
                    product.title[:40] + "..." if len(product.title) > 40 else product.title,
                    f"${product.price:.2f}",
                    product.affiliate_url[:30] + "...",
                )

            console.print(table)
        else:
            console.print("[yellow]No products found for comparison[/yellow]")

    def get_trending_deals(self):
        """Get trending deals across platforms."""
        console.print("\n[bold cyan]Fetching trending deals...[/bold cyan]")

        deals = self.product_manager.get_best_deals(min_discount=20.0)

        if deals:
            table = Table(title="Best Deals")
            table.add_column("Platform", style="cyan")
            table.add_column("Product", style="white", no_wrap=False)
            table.add_column("Price", style="green")
            table.add_column("Discount", style="red")

            for deal in deals[:10]:  # Top 10 deals
                table.add_row(
                    deal.platform,
                    deal.title[:40] + "..." if len(deal.title) > 40 else deal.title,
                    f"${deal.price:.2f}",
                    f"{deal.discount_percentage:.0f}% OFF",
                )

            console.print(table)
        else:
            console.print("[yellow]No deals found[/yellow]")

    def generate_content(self, product_id: str, platform: str):
        """Generate content for a product."""
        if not self.content_generator:
            console.print(
                "[red]Content generation not available. Please configure OpenAI API key.[/red]"
            )
            return

        product = self.product_manager.providers[platform].get_product_details(product_id)

        if product:
            console.print(f"\n[bold cyan]Generating content for:[/bold cyan] {product.title}")

            # Generate description
            description = self.content_generator.generate_product_description(product)
            console.print("\n[bold]Generated Description:[/bold]")
            console.print(description)

            # Generate social media post
            social_post = self.content_generator.generate_social_media_post(product, "twitter")
            console.print("\n[bold]Twitter Post:[/bold]")
            console.print(social_post)

            # Save to database
            self.product_manager.save_product(product)
            console.print("\n[green]Product saved to database![/green]")

    def schedule_posts(self):
        """Schedule social media posts."""
        if not self.social_media_poster:
            console.print(
                "[red]Social media posting not available. Please configure API keys.[/red]"
            )
            return

        # Get saved products
        products = self.product_manager.get_saved_products()

        if products:
            console.print(f"\n[bold cyan]Scheduling posts for {len(products)} products[/bold cyan]")
            self.social_media_poster.schedule_product_posts(products)

            if Confirm.ask("Start scheduler?"):
                self.social_media_poster.run_scheduler()
        else:
            console.print("[yellow]No products in database to schedule[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="Affiliate Marketing Automation System")
    parser.add_argument(
        "command",
        choices=["search", "compare", "deals", "generate", "schedule"],
        help="Command to execute",
    )
    parser.add_argument("--query", "-q", help="Search query or product name")
    parser.add_argument("--product-id", "-p", help="Product ID for content generation")
    parser.add_argument("--platform", "-pl", help="Platform name (amazon, flipkart)")

    args = parser.parse_args()

    automation = AffiliateAutomation()

    try:
        if args.command == "search":
            if not args.query:
                args.query = Prompt.ask("Enter search query")
            automation.search_products(args.query)

        elif args.command == "compare":
            if not args.query:
                args.query = Prompt.ask("Enter product name to compare")
            automation.compare_prices(args.query)

        elif args.command == "deals":
            automation.get_trending_deals()

        elif args.command == "generate":
            if not args.product_id:
                args.product_id = Prompt.ask("Enter product ID")
            if not args.platform:
                args.platform = Prompt.ask("Enter platform", choices=["amazon", "flipkart"])
            automation.generate_content(args.product_id, args.platform)

        elif args.command == "schedule":
            automation.schedule_posts()

    except KeyboardInterrupt:
        console.print("\n[red]Operation cancelled by user[/red]")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
