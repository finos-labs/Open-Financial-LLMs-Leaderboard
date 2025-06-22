import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from huggingface_hub import HfApi
from dotenv import load_dotenv

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent.parent
ROOT_DIR = BACKEND_DIR.parent

# Load environment variables from .env file in root directory
load_dotenv(ROOT_DIR / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Hugging Face API
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in environment variables")
api = HfApi(token=HF_TOKEN)

# Default organization
HF_ORGANIZATION = os.getenv('HF_ORGANIZATION', 'TheFinAI')

def get_last_votes(limit: int = 5) -> List[Dict]:
    """Get the last votes from the votes dataset"""
    try:
        logger.info("\nFetching last votes...")
        
        # Download and read votes file
        logger.info("Downloading votes file...")
        votes_file = api.hf_hub_download(
            repo_id=f"{HF_ORGANIZATION}/votes",
            filename="votes_data.jsonl",
            repo_type="dataset"
        )
        
        logger.info("Reading votes file...")
        votes = []
        with open(votes_file, 'r') as f:
            for line in f:
                try:
                    vote = json.loads(line)
                    votes.append(vote)
                except json.JSONDecodeError:
                    continue
        
        # Sort by timestamp and get last n votes
        logger.info("Sorting votes...")
        votes.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        last_votes = votes[:limit]
        
        logger.info(f"✓ Found {len(last_votes)} recent votes")
        return last_votes
        
    except Exception as e:
        logger.error(f"Error reading votes: {str(e)}")
        return []

def get_last_models(limit: int = 5) -> List[Dict]:
    """Get the last models from the requests dataset using commit history"""
    try:
        logger.info("\nFetching last model submissions...")
        
        # Get commit history
        logger.info("Getting commit history...")
        commits = list(api.list_repo_commits(
            repo_id=f"{HF_ORGANIZATION}/requests",
            repo_type="dataset"
        ))
        logger.info(f"Found {len(commits)} commits")
        
        # Track processed files to avoid duplicates
        processed_files = set()
        models = []
        
        # Process commits until we have enough models
        for i, commit in enumerate(commits):
            logger.info(f"Processing commit {i+1}/{len(commits)} ({commit.created_at})")
            
            # Look at added/modified files in this commit
            files_to_process = [f for f in (commit.added + commit.modified) if f.endswith('.json')]
            if files_to_process:
                logger.info(f"Found {len(files_to_process)} JSON files in commit")
            
            for file in files_to_process:
                if file in processed_files:
                    continue
                    
                processed_files.add(file)
                logger.info(f"Downloading {file}...")
                
                try:
                    # Download and read the file
                    content = api.hf_hub_download(
                        repo_id=f"{HF_ORGANIZATION}/requests",
                        filename=file,
                        repo_type="dataset"
                    )
                    
                    with open(content, 'r') as f:
                        model_data = json.load(f)
                        models.append(model_data)
                        logger.info(f"✓ Added model {model_data.get('model', 'Unknown')}")
                        
                        if len(models) >= limit:
                            logger.info("Reached desired number of models")
                            break
                            
                except Exception as e:
                    logger.error(f"Error reading file {file}: {str(e)}")
                    continue
                    
            if len(models) >= limit:
                break
        
        logger.info(f"✓ Found {len(models)} recent model submissions")
        return models
        
    except Exception as e:
        logger.error(f"Error reading models: {str(e)}")
        return []

def main():
    """Display last activities from the leaderboard"""
    try:
        # Get last votes
        logger.info("\n=== Last Votes ===")
        last_votes = get_last_votes()
        if last_votes:
            for vote in last_votes:
                logger.info(f"\nModel: {vote.get('model')}")
                logger.info(f"User: {vote.get('username')}")
                logger.info(f"Timestamp: {vote.get('timestamp')}")
        else:
            logger.info("No votes found")
        
        # Get last model submissions
        logger.info("\n=== Last Model Submissions ===")
        last_models = get_last_models()
        if last_models:
            for model in last_models:
                logger.info(f"\nModel: {model.get('model')}")
                logger.info(f"Submitter: {model.get('sender', 'Unknown')}")
                logger.info(f"Status: {model.get('status', 'Unknown')}")
                logger.info(f"Submission Time: {model.get('submitted_time', 'Unknown')}")
                logger.info(f"Precision: {model.get('precision', 'Unknown')}")
                logger.info(f"Weight Type: {model.get('weight_type', 'Unknown')}")
        else:
            logger.info("No models found")
            
    except Exception as e:
        logger.error(f"Global error: {str(e)}")

if __name__ == "__main__":
    main() 
