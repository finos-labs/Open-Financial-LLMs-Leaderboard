from fastapi import FastAPI
from app.config.logging_config import setup_logging
import logging

# Initialize logging configuration
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Open Greek Financial LLM Leaderboard API")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")

# Import and include routers after app initialization
from app.api import models, votes
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(votes.router, prefix="/api", tags=["votes"]) 
