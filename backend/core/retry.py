import asyncio
from typing import Callable, Any, TypeVar
from functools import wraps
from core.logger import logger

T = TypeVar('T')

class RetryHandler:
    """
    Provides a retry mechanism for async LLM calls.
    Handles temporary API failures, rate limits, or validation errors.
    """
    
    @staticmethod
    def with_retries(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0):
        """
        Decorator that retries the wrapped async function on failure.
        Uses exponential backoff for delays.
        """
        def decorator(func: Callable[..., Any]):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                delay = base_delay
                last_exception = None
                
                for attempt in range(1, max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        logger.warning(
                            f"Attempt {attempt}/{max_retries} failed for {func.__name__}: {str(e)}"
                        )
                        
                        if attempt == max_retries:
                            break
                            
                        logger.info(f"Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        
                        # Exponential backoff
                        delay = min(delay * 2, max_delay)
                
                logger.error(f"All {max_retries} attempts failed for {func.__name__}.")
                raise last_exception
            return wrapper
        return decorator
