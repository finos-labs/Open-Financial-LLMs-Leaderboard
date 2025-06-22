from fastapi import Depends, HTTPException
import logging
from app.services.models import ModelService
from app.services.votes import VoteService
from app.utils.logging import LogFormatter

logger = logging.getLogger(__name__)

model_service = ModelService()
vote_service = VoteService()

async def get_model_service() -> ModelService:
    """Dependency to get ModelService instance"""
    try:
        logger.info(LogFormatter.info("Initializing model service dependency"))
        await model_service.initialize()
        logger.info(LogFormatter.success("Model service initialized"))
        return model_service
    except Exception as e:
        error_msg = "Failed to initialize model service"
        logger.error(LogFormatter.error(error_msg, e))
        raise HTTPException(status_code=500, detail=str(e))

async def get_vote_service() -> VoteService:
    """Dependency to get VoteService instance"""
    try:
        logger.info(LogFormatter.info("Initializing vote service dependency"))
        await vote_service.initialize()
        logger.info(LogFormatter.success("Vote service initialized"))
        return vote_service
    except Exception as e:
        error_msg = "Failed to initialize vote service"
        logger.error(LogFormatter.error(error_msg, e))
        raise HTTPException(status_code=500, detail=str(e)) 