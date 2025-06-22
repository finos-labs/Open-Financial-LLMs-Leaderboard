import os
import json
import logging
from datetime import datetime
from pathlib import Path
from huggingface_hub import HfApi
from dotenv import load_dotenv
from app.config.hf_config import HF_ORGANIZATION

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

def count_evaluated_models():
    """Count the number of evaluated models"""
    try:
        # Get dataset info
        dataset_info = api.dataset_info(repo_id=f"{HF_ORGANIZATION}/greek-contents", repo_type="dataset")
        
        # Get file list
        files = api.list_repo_files(f"{HF_ORGANIZATION}/greek-contents", repo_type="dataset")
        
        # Get last commit info
        commits = api.list_repo_commits(f"{HF_ORGANIZATION}/greek-contents", repo_type="dataset")
        last_commit = next(commits, None)
        
        # Count lines in jsonl files
        total_entries = 0
        for file in files:
            if file.endswith('.jsonl'):
                try:
                    # Download file content
                    content = api.hf_hub_download(
                        repo_id=f"{HF_ORGANIZATION}/greek-contents",
                        filename=file,
                        repo_type="dataset"
                    )
                    
                    # Count lines
                    with open(content, 'r') as f:
                        for _ in f:
                            total_entries += 1
                            
                except Exception as e:
                    logger.error(f"Error processing file {file}: {str(e)}")
                    continue
        
        # Build response
        response = {
            "total_models": total_entries,
            "last_modified": last_commit.created_at if last_commit else None,
            "file_count": len(files),
            "size_bytes": dataset_info.size_in_bytes,
            "downloads": dataset_info.downloads
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error counting evaluated models: {str(e)}")
        return {
            "error": str(e)
        }

def main():
    """Main function to count evaluated models"""
    try:
        logger.info("\nAnalyzing evaluated models...")
        result = count_evaluated_models()
        
        if 'error' in result:
            logger.error(f"❌ Error: {result['error']}")
        else:
            logger.info(f"✓ {result['total_models']} models evaluated")
            logger.info(f"✓ {result['file_count']} files")
            logger.info(f"✓ {result['size_bytes'] / 1024:.1f} KB")
            logger.info(f"✓ {result['downloads']} downloads")
            
            if result['last_modified']:
                last_modified = datetime.fromisoformat(result['last_modified'].replace('Z', '+00:00'))
                logger.info(f"✓ Last modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return result
            
    except Exception as e:
        logger.error(f"Global error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    main() 
