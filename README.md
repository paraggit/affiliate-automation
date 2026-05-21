# Affiliate Marketing Automation System

A flexible, modular Python system for automating affiliate marketing across multiple platforms. Search products, compare prices, generate AI-powered content, and schedule social media posts — all from the command line.

## Features

- **Multi-Platform Support** — Amazon and Flipkart affiliate integrations with a pluggable architecture for adding more
- **Product Search & Comparison** — Search across platforms and compare prices side-by-side
- **AI Content Generation** — Generate product descriptions, social media posts, and comparison articles using OpenAI (GPT-4o-mini)
- **Social Media Automation** — Schedule and post to Twitter with image support, expandable to other platforms
- **Database Storage** — SQLAlchemy-backed product persistence with upsert support
- **Retry with Backoff** — Automatic exponential backoff on network failures for all API calls and web scraping
- **Rich CLI** — Formatted tables and interactive prompts via [Rich](https://github.com/Textualize/rich)

## Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

1. Clone the repository:

```bash
git clone https://github.com/paraggit/affiliate-automation.git
cd affiliate-automation
```

2. Install dependencies:

```bash
poetry install
```

3. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

| Variable | Description |
|---|---|
| `AMAZON_ASSOCIATE_TAG` | Amazon Associates partner tag |
| `AMAZON_ACCESS_KEY` | Amazon Product Advertising API access key |
| `AMAZON_SECRET_KEY` | Amazon Product Advertising API secret key |
| `FLIPKART_AFFILIATE_ID` | Flipkart Affiliate ID |
| `FLIPKART_AFFILIATE_TOKEN` | Flipkart Affiliate API token |
| `OPENAI_API_KEY` | OpenAI API key for content generation |
| `TWITTER_API_KEY` | Twitter API key |
| `TWITTER_API_SECRET` | Twitter API secret |
| `TWITTER_ACCESS_TOKEN` | Twitter access token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret |
| `DATABASE_URL` | Database connection string (default: `sqlite:///affiliate_data.db`) |

## Usage

### Search Products

Search across all configured platforms:

```bash
poetry run python main.py search -q "wireless headphones"
```

### Compare Prices

Compare the same product across platforms:

```bash
poetry run python main.py compare -q "iPhone 15"
```

### Get Trending Deals

Fetch products with 20%+ discounts:

```bash
poetry run python main.py deals
```

### Generate Content

Generate AI-powered descriptions and social media posts for a product:

```bash
poetry run python main.py generate -p "B08N5WRWNW" -pl "amazon"
```

### Schedule Social Media Posts

Schedule automatic Twitter posts for saved products (posts at 09:00, 14:00, 19:00):

```bash
poetry run python main.py schedule
```

## Architecture

```
affiliate-automation/
├── main.py                          # CLI entry point
├── config/
│   └── settings.py                  # Pydantic settings (env-based config)
├── src/
│   ├── core/
│   │   ├── base_affiliate.py        # Product dataclass & BaseAffiliateProvider ABC
│   │   └── product_manager.py       # Multi-platform orchestrator
│   ├── platforms/
│   │   ├── amazon/
│   │   │   └── amazon_affiliate.py  # Amazon provider (web scraping)
│   │   └── flipkart/
│   │       └── flipkart_affiliate.py # Flipkart provider (API-based)
│   ├── automation/
│   │   ├── content_generator.py     # OpenAI-powered content generation
│   │   └── social_media_poster.py   # Twitter posting & scheduling
│   └── utils/
│       ├── database.py              # SQLAlchemy models & Database class
│       ├── logger.py                # Rich console + file logging
│       └── retry.py                 # Exponential backoff retry decorator
└── tests/
    ├── test_amazon.py
    ├── test_flipkart.py
    ├── test_content_generator.py
    ├── test_database.py
    ├── test_product_manager.py
    └── test_retry.py
```

### Key Design Decisions

- **Abstract base class** (`BaseAffiliateProvider`) defines the contract all platforms must implement: `search_products`, `get_product_details`, `generate_affiliate_link`, `get_trending_products`
- **ProductManager** orchestrates searches across all enabled providers and handles database persistence
- **Pydantic Settings** loads configuration from `.env` with type validation
- **Retry decorator** (`@retry_on_failure`) wraps network calls with configurable max retries and exponential backoff

## Adding New Platforms

1. Create a new module in `src/platforms/<platform_name>/`:

```python
# src/platforms/myntra/myntra_affiliate.py
from ...core.base_affiliate import BaseAffiliateProvider, Product

class MyntraAffiliate(BaseAffiliateProvider):
    def get_required_config_fields(self) -> list[str]:
        return ["myntra_affiliate_id"]

    def search_products(self, query: str, **kwargs) -> list[Product]:
        # Implement search logic
        ...

    def get_product_details(self, product_id: str) -> Product | None:
        ...

    def generate_affiliate_link(self, product_url: str) -> str:
        ...

    def get_trending_products(self, category: str | None = None) -> list[Product]:
        ...
```

2. Register it in `src/core/product_manager.py` inside `_initialize_providers()`
3. Add credentials to `.env.example`

## Development

### Run Tests

```bash
poetry run pytest -v
```

### Run Tests with Coverage

```bash
poetry run pytest --cov=src --cov-report=html --cov-report=term
```

### Format Code

```bash
poetry run isort src/ tests/
poetry run black src/ tests/
```

### Lint

```bash
poetry run flake8 src/ tests/
poetry run bandit -r src/ -ll
```

### Run All Checks

```bash
make check
```

See `make help` for all available commands.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and add tests
4. Run `make check` to verify formatting, linting, and tests pass
5. Commit and push your branch
6. Open a pull request

## License

MIT License — see [LICENSE](LICENSE) for details.
