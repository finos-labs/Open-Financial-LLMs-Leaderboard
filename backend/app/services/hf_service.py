from typing import Optional
from huggingface_hub import HfApi
from app.config import HF_TOKEN, API
from app.core.cache import cache_config
from app.utils.logging import LogFormatter
import logging

logger = logging.getLogger(__name__)

class HuggingFaceService:
    def __init__(self):
        self.api = API
        self.token = HF_TOKEN
        self.cache_dir = cache_config.models_cache

    async def check_authentication(self) -> bool:
        """Check if the HF token is valid"""
        if not self.token:
            return False
        try:
            logger.info(LogFormatter.info("Checking HF token validity..."))
            self.api.get_token_permission()
            logger.info(LogFormatter.success("HF token is valid"))
            return True
        except Exception as e:
            logger.error(LogFormatter.error("HF token validation failed", e))
            return False

    async def get_user_info(self) -> Optional[dict]:
        """Get information about the authenticated user"""
        try:
            logger.info(LogFormatter.info("Fetching user information..."))
            info = self.api.get_token_permission()
            logger.info(LogFormatter.success(f"User info retrieved for: {info.get('user', 'Unknown')}"))
            return info
        except Exception as e:
            logger.error(LogFormatter.error("Failed to get user info", e))
            return None

    def _log_repo_operation(self, operation: str, repo: str, details: str = None):
        """Helper to log repository operations"""
        logger.info(LogFormatter.section(f"HF REPOSITORY OPERATION - {operation.upper()}"))
        stats = {
            "Operation": operation,
            "Repository": repo,
        }
        if details:
            stats["Details"] = details
        for line in LogFormatter.tree(stats):
            logger.info(line) 