from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.leaderboard import LeaderboardService
from app.core.fastapi_cache import cached, build_cache_key
import logging
from app.utils.logging import LogFormatter

logger = logging.getLogger(__name__)
router = APIRouter()
leaderboard_service = LeaderboardService()

def leaderboard_key_builder(func, namespace: str = "leaderboard", **kwargs):
    """Build cache key for leaderboard data"""
    key_type = "raw" if func.__name__ == "get_leaderboard" else "formatted"
    key = build_cache_key(namespace, key_type)
    logger.debug(LogFormatter.info(f"Built leaderboard cache key: {key}"))
    return key

@router.get("")
@cached(expire=300, key_builder=leaderboard_key_builder)
async def get_leaderboard() -> List[Dict[str, Any]]:
    """
    Get raw leaderboard data
    Response will be automatically GZIP compressed if size > 500 bytes
    """
    try:
        logger.info(LogFormatter.info("Fetching raw leaderboard data"))
        data = await leaderboard_service.fetch_raw_data()
        logger.info(LogFormatter.success(f"Retrieved {len(data)} leaderboard entries"))
        return data
    except Exception as e:
        logger.error(LogFormatter.error("Failed to fetch raw leaderboard data", e))
        raise

@router.get("/formatted")
@cached(expire=300, key_builder=leaderboard_key_builder)
async def get_formatted_leaderboard() -> List[Dict[str, Any]]:
    """
    Get formatted leaderboard data with restructured objects
    Response will be automatically GZIP compressed if size > 500 bytes
    """
    try:
        logger.info(LogFormatter.info("Fetching formatted leaderboard data"))
        data = await leaderboard_service.get_formatted_data()
        logger.info(LogFormatter.success(f"Retrieved {len(data)} formatted entries"))
        return data
    except Exception as e:
        logger.error(LogFormatter.error("Failed to fetch formatted leaderboard data", e))
        raise 