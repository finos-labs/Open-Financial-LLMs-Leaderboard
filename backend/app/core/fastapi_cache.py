from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from datetime import timedelta
from app.config import CACHE_TTL
import logging
from app.utils.logging import LogFormatter

logger = logging.getLogger(__name__)

def setup_cache():
    """Initialize FastAPI Cache with in-memory backend"""
    FastAPICache.init(
        backend=InMemoryBackend(),
        prefix="fastapi-cache",
        expire=CACHE_TTL
    )
    logger.info(LogFormatter.success("FastAPI Cache initialized with in-memory backend"))

def invalidate_cache_key(key: str):
    """Invalidate a specific cache key"""
    try:
        backend = FastAPICache.get_backend()
        if hasattr(backend, 'delete'):
            backend.delete(key)
            logger.info(LogFormatter.success(f"Cache invalidated for key: {key}"))
        else:
            logger.warning(LogFormatter.warning("Cache backend does not support deletion"))
    except Exception as e:
        logger.error(LogFormatter.error(f"Failed to invalidate cache key: {key}", e))

def build_cache_key(namespace: str, *args) -> str:
    """Build a consistent cache key"""
    key = f"fastapi-cache:{namespace}:{':'.join(str(arg) for arg in args)}"
    logger.debug(LogFormatter.info(f"Built cache key: {key}"))
    return key

def cached(expire: int = CACHE_TTL, key_builder=None):
    """Decorator for caching endpoint responses
    
    Args:
        expire (int): Cache TTL in seconds
        key_builder (callable, optional): Custom key builder function
    """
    return cache(
        expire=expire,
        key_builder=key_builder
    ) 