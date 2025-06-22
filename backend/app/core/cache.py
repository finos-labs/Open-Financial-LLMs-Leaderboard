import os
import shutil
from pathlib import Path
from datetime import timedelta
import logging
from app.utils.logging import LogFormatter
from app.config.base import (
    CACHE_ROOT,
    DATASETS_CACHE,
    MODELS_CACHE,
    VOTES_CACHE,
    EVAL_CACHE,
    CACHE_TTL
)

logger = logging.getLogger(__name__)

class CacheConfig:
    def __init__(self):
        # Get cache paths from config
        self.cache_root = CACHE_ROOT
        self.datasets_cache = DATASETS_CACHE
        self.models_cache = MODELS_CACHE
        self.votes_cache = VOTES_CACHE
        self.eval_cache = EVAL_CACHE
        
        # Specific files
        self.votes_file = self.votes_cache / "votes_data.jsonl"
        self.eval_requests_file = self.eval_cache / "eval_requests.jsonl"
        
        # Cache TTL
        self.cache_ttl = timedelta(seconds=CACHE_TTL)
        
        self._initialize_cache_dirs()
        self._setup_environment()
        
    def _initialize_cache_dirs(self):
        """Initialize all necessary cache directories"""
        try:
            logger.info(LogFormatter.section("CACHE INITIALIZATION"))
            
            cache_dirs = {
                "Root": self.cache_root,
                "Datasets": self.datasets_cache,
                "Models": self.models_cache,
                "Votes": self.votes_cache,
                "Eval": self.eval_cache
            }
            
            for name, cache_dir in cache_dirs.items():
                cache_dir.mkdir(parents=True, exist_ok=True)
                logger.info(LogFormatter.success(f"{name} cache directory: {cache_dir}"))
                
        except Exception as e:
            logger.error(LogFormatter.error("Failed to create cache directories", e))
            raise
            
    def _setup_environment(self):
        """Configure HuggingFace environment variables"""
        logger.info(LogFormatter.subsection("ENVIRONMENT SETUP"))
        
        env_vars = {
            "HF_HOME": str(self.cache_root),
            "TRANSFORMERS_CACHE": str(self.models_cache),
            "HF_DATASETS_CACHE": str(self.datasets_cache)
        }
        
        for var, value in env_vars.items():
            os.environ[var] = value
            logger.info(LogFormatter.info(f"Set {var}={value}"))
        
    def get_cache_path(self, cache_type: str) -> Path:
        """Returns the path for a specific cache type"""
        cache_paths = {
            "datasets": self.datasets_cache,
            "models": self.models_cache,
            "votes": self.votes_cache,
            "eval": self.eval_cache
        }
        return cache_paths.get(cache_type, self.cache_root)

    def flush_cache(self, cache_type: str = None):
        """Flush specified cache or all caches if no type is specified"""
        try:
            if cache_type:
                logger.info(LogFormatter.section(f"FLUSHING {cache_type.upper()} CACHE"))
                cache_dir = self.get_cache_path(cache_type)
                if cache_dir.exists():
                    stats = {
                        "Cache_Type": cache_type,
                        "Directory": str(cache_dir)
                    }
                    for line in LogFormatter.tree(stats, "Cache Details"):
                        logger.info(line)
                    shutil.rmtree(cache_dir)
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(LogFormatter.success("Cache cleared successfully"))
            else:
                logger.info(LogFormatter.section("FLUSHING ALL CACHES"))
                for cache_type in ["datasets", "models", "votes", "eval"]:
                    self.flush_cache(cache_type)
                logger.info(LogFormatter.success("All caches cleared successfully"))
                
        except Exception as e:
            logger.error(LogFormatter.error("Failed to flush cache", e))
            raise

# Singleton instance of cache configuration
cache_config = CacheConfig() 