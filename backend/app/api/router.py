from fastapi import APIRouter

from app.api.endpoints import leaderboard, votes, models

router = APIRouter()

router.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
router.include_router(votes.router, prefix="/votes", tags=["votes"])
router.include_router(models.router, prefix="/models", tags=["models"]) 