"""
Hugging Face configuration module
"""
import os
import logging
from typing import Optional
from huggingface_hub import HfApi
from pathlib import Path
from app.core.cache import cache_config
from app.utils.logging import LogFormatter

logger = logging.getLogger(__name__)

# Organization or user who owns the datasets
HF_ORGANIZATION = "TheFinAI"

# Get HF token directly from environment
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    logger.warning("HF_TOKEN not found in environment variables. Some features may be limited.")

# Initialize HF API
API = HfApi(token=HF_TOKEN)

# Repository configuration
QUEUE_REPO = f"{HF_ORGANIZATION}/requests"
AGGREGATED_REPO = f"{HF_ORGANIZATION}/greek-contents"
VOTES_REPO = f"{HF_ORGANIZATION}/votes"
MAINTAINERS_HIGHLIGHT_REPO = f"{HF_ORGANIZATION}/maintainers-highlight"

# File paths from cache config
VOTES_PATH = cache_config.votes_file
EVAL_REQUESTS_PATH = cache_config.eval_requests_file
MODEL_CACHE_DIR = cache_config.models_cache
