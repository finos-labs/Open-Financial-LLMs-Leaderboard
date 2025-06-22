from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, List
from app.services.votes import VoteService
from app.core.fastapi_cache import cached, build_cache_key, invalidate_cache_key
import logging
from app.utils.logging import LogFormatter

logger = logging.getLogger(__name__)
router = APIRouter()
vote_service = VoteService()

def model_votes_key_builder(func, namespace: str = "model_votes", **kwargs):
    """Build cache key for model votes"""
    provider = kwargs.get('provider')
    model = kwargs.get('model')
    key = build_cache_key(namespace, provider, model)
    logger.debug(LogFormatter.info(f"Built model votes cache key: {key}"))
    return key

def user_votes_key_builder(func, namespace: str = "user_votes", **kwargs):
    """Build cache key for user votes"""
    user_id = kwargs.get('user_id')
    key = build_cache_key(namespace, user_id)
    logger.debug(LogFormatter.info(f"Built user votes cache key: {key}"))
    return key

@router.post("/{model_id:path}")
async def add_vote(
    model_id: str,
    vote_type: str = Query(..., description="Type of vote (up/down)"),
    user_id: str = Query(..., description="HuggingFace username")
) -> Dict[str, Any]:
    try:
        logger.info(LogFormatter.section("ADDING VOTE"))
        stats = {
            "Model": model_id,
            "User": user_id,
            "Type": vote_type
        }
        for line in LogFormatter.tree(stats, "Vote Details"):
            logger.info(line)
        
        await vote_service.initialize()
        result = await vote_service.add_vote(model_id, user_id, vote_type)
        
        # Invalidate affected caches
        try:
            logger.info(LogFormatter.subsection("CACHE INVALIDATION"))
            provider, model = model_id.split('/', 1)
            
            # Build and invalidate cache keys
            model_cache_key = build_cache_key("model_votes", provider, model)
            user_cache_key = build_cache_key("user_votes", user_id)
            
            invalidate_cache_key(model_cache_key)
            invalidate_cache_key(user_cache_key)
            
            cache_stats = {
                "Model_Cache": model_cache_key,
                "User_Cache": user_cache_key
            }
            for line in LogFormatter.tree(cache_stats, "Invalidated Caches"):
                logger.info(line)
                
        except Exception as e:
            logger.error(LogFormatter.error("Failed to invalidate cache", e))
        
        return result
    except Exception as e:
        logger.error(LogFormatter.error("Failed to add vote", e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/model/{provider}/{model}")
@cached(expire=60, key_builder=model_votes_key_builder)
async def get_model_votes(
    provider: str, 
    model: str
) -> Dict[str, Any]:
    """Get all votes for a specific model"""
    try:
        logger.info(LogFormatter.info(f"Fetching votes for model: {provider}/{model}"))
        await vote_service.initialize()
        model_id = f"{provider}/{model}"
        result = await vote_service.get_model_votes(model_id)
        logger.info(LogFormatter.success(f"Found {result.get('total_votes', 0)} votes"))
        return result
    except Exception as e:
        logger.error(LogFormatter.error("Failed to get model votes", e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user/{user_id}")
@cached(expire=60, key_builder=user_votes_key_builder)
async def get_user_votes(
    user_id: str
) -> List[Dict[str, Any]]:
    """Get all votes from a specific user"""
    try:
        logger.info(LogFormatter.info(f"Fetching votes for user: {user_id}"))
        await vote_service.initialize()
        votes = await vote_service.get_user_votes(user_id)
        logger.info(LogFormatter.success(f"Found {len(votes)} votes"))
        return votes
    except Exception as e:
        logger.error(LogFormatter.error("Failed to get user votes", e))
        raise HTTPException(status_code=400, detail=str(e)) 