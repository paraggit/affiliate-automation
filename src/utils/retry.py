import time
from functools import wraps
from typing import Tuple, Type

from .logger import get_logger

logger = get_logger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """Retry a function with exponential backoff."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}), "
                            f"retrying in {delay}s: {e}"
                        )
                        time.sleep(delay)
            logger.error(f"{func.__name__} failed after {max_retries} attempts: {last_exception}")
            raise last_exception

        return wrapper

    return decorator
