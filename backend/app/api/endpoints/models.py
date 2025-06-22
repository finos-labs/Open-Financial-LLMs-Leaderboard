from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
from app.services.models import ModelService
from app.api.dependencies import get_model_service
from app.core.fastapi_cache import cached
from app.utils.logging import LogFormatter

logger = logging.getLogger(__name__)
router = APIRouter(tags=["models"])

@router.get("/status")
@cached(expire=300)
async def get_models_status(
    model_service: ModelService = Depends(get_model_service)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get all models grouped by status"""
    try:
        logger.info(LogFormatter.info("Fetching status for all models"))
        result = await model_service.get_models()
        stats = {
            status: len(models) for status, models in result.items()
        }
        for line in LogFormatter.stats(stats, "Models by Status"):
            logger.info(line)
        return result
    except Exception as e:
        logger.error(LogFormatter.error("Failed to get models status", e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
@cached(expire=60)
async def get_pending_models(
    model_service: ModelService = Depends(get_model_service)
) -> List[Dict[str, Any]]:
    """Get all models waiting for evaluation"""
    try:
        logger.info(LogFormatter.info("Fetching pending models"))
        models = await model_service.get_models()
        pending = models.get("pending", [])
        logger.info(LogFormatter.success(f"Found {len(pending)} pending models"))
        return pending
    except Exception as e:
        logger.error(LogFormatter.error("Failed to get pending models", e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit")
async def submit_model(
    model_data: Dict[str, Any],
    model_service: ModelService = Depends(get_model_service)
) -> Dict[str, Any]:
    try:
        logger.info(LogFormatter.section("MODEL SUBMISSION"))
        
        user_id = model_data.pop('user_id', None)
        if not user_id:
            error_msg = "user_id is required"
            logger.error(LogFormatter.error("Validation failed", error_msg))
            raise ValueError(error_msg)
            
        # Log submission details
        submission_info = {
            "Model_ID": model_data.get("model_id"),
            "User": user_id,
            "Base_Model": model_data.get("base_model"),
            "Precision": model_data.get("precision"),
            "Model_Type": model_data.get("model_type")
        }
        for line in LogFormatter.tree(submission_info, "Submission Details"):
            logger.info(line)
            
        result = await model_service.submit_model(model_data, user_id)
        logger.info(LogFormatter.success("Model submitted successfully"))
        return result
        
    except ValueError as e:
        logger.error(LogFormatter.error("Invalid submission data", e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(LogFormatter.error("Submission failed", e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{model_id}/status")
async def get_model_status(
    model_id: str,
    model_service: ModelService = Depends(get_model_service)
) -> Dict[str, Any]:
    try:
        logger.info(LogFormatter.info(f"Checking status for model: {model_id}"))
        status = await model_service.get_model_status(model_id)
        
        if status["status"] != "not_found":
            logger.info(LogFormatter.success("Status found"))
            for line in LogFormatter.tree(status, "Model Status"):
                logger.info(line)
        else:
            logger.warning(LogFormatter.warning(f"No status found for model: {model_id}"))
            
        return status
        
    except Exception as e:
        logger.error(LogFormatter.error("Failed to get model status", e))
        raise HTTPException(status_code=500, detail=str(e)) 