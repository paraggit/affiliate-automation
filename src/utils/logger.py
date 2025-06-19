import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Console handler with Rich
    console_handler = RichHandler(console=console, show_time=True, show_path=False)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = logging.FileHandler(log_dir / "affiliate_automation.log", mode='a')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
