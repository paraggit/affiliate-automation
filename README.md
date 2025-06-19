# Affiliate Marketing Automation System

A flexible, modular Python system for automating affiliate marketing across multiple platforms.

## Features

- **Multi-Platform Support**: Currently supports Amazon and Flipkart, with easy extensibility for other platforms
- **Product Search & Comparison**: Search and compare products across platforms
- **Content Generation**: AI-powered product descriptions and social media posts
- **Social Media Automation**: Schedule and post to Twitter (expandable to other platforms)
- **Database Storage**: Track products and performance
- **Modular Architecture**: Easy to add new affiliate platforms

## Installation

1. Install Poetry if you haven't already:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository:

```bash
git clone <your-repo-url>
cd affiliate-automation
```

3. Install dependencies:

```bash
poetry install
```

4. Copy `.env.example` to `.env` and fill in your API credentials:

```bash
cp .env.example .env
```

## Usage

### Search Products

```bash
poetry run python main.py search -q "laptop"
```

### Compare Prices

```bash
poetry run python main.py compare -q "iPhone 15"
```

### Get Trending Deals

```bash
poetry run python main.py deals
```

### Generate Content

```bash
poetry run python main.py generate -p "ASIN123" -pl "amazon"
```

### Schedule Social Media Posts

```bash
poetry run python main.py schedule
```

## Adding New Platforms

1. Create a new module in `src/platforms/<platform_name>/`
2. Implement the `BaseAffiliateProvider` abstract class
3. Add initialization in `ProductManager._initialize_providers()`
4. Update `.env.example` with required credentials

Example for adding Mesho:

```python
# src/platforms/mesho/mesho_affiliate.py
from ...core.base_affiliate import BaseAffiliateProvider, Product

class MeshoAffiliate(BaseAffiliateProvider):
    def search_products(self, query: str, **kwargs) -> List[Product]:
        # Implement Mesho API search
        pass

    # Implement other required methods
```

## Testing

Run tests with:

```bash
poetry run pytest
```

## Development

Format code:

```bash
poetry run black .
```

Lint code:

```bash
poetry run flake8
```

## Architecture

- **Core**: Base classes and interfaces
- **Platforms**: Platform-specific implementations
- **Automation**: Content generation and posting
- **Utils**: Database, logging, and helpers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## License

MIT License
