import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
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

def analyze_dataset(repo_id: str) -> Dict[str, Any]:
    """Analyze a dataset and return statistics"""
    try:
        # Get dataset info
        dataset_info = api.dataset_info(repo_id=repo_id)
        
        # Get file list
        files = api.list_repo_files(repo_id, repo_type="dataset")
        
        # Get last commit info
        commits = api.list_repo_commits(repo_id, repo_type="dataset")
        last_commit = next(commits, None)
        
        # Count lines in jsonl files
        total_entries = 0
        for file in files:
            if file.endswith('.jsonl'):
                try:
                    # Download file content
                    content = api.hf_hub_download(
                        repo_id=repo_id,
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
        
        # Special handling for requests dataset
        if repo_id == f"{HF_ORGANIZATION}/requests":
            pending_count = 0
            completed_count = 0
            
            try:
                content = api.hf_hub_download(
                    repo_id=repo_id,
                    filename="eval_requests.jsonl",
                    repo_type="dataset"
                )
                
                with open(content, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            if entry.get("status") == "pending":
                                pending_count += 1
                            elif entry.get("status") == "completed":
                                completed_count += 1
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                logger.error(f"Error analyzing requests: {str(e)}")
        
        # Build response
        response = {
            "id": repo_id,
            "last_modified": last_commit.created_at if last_commit else None,
            "total_entries": total_entries,
            "file_count": len(files),
            "size_bytes": dataset_info.size_in_bytes,
            "downloads": dataset_info.downloads,
        }
        
        # Add request-specific info if applicable
        if repo_id == f"{HF_ORGANIZATION}/requests":
            response.update({
                "pending_requests": pending_count,
                "completed_requests": completed_count
            })
            
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing dataset {repo_id}: {str(e)}")
        return {
            "id": repo_id,
            "error": str(e)
        }

def main():
    """Main function to analyze all datasets"""
    try:
        # List of datasets to analyze
        datasets = [
            {
                "id": f"{HF_ORGANIZATION}/contents",
                "description": "Aggregated results"
            },
            {
                "id": f"{HF_ORGANIZATION}/requests",
                "description": "Evaluation requests"
            },
            {
                "id": f"{HF_ORGANIZATION}/votes",
                "description": "User votes"
            },
            {
                "id": f"{HF_ORGANIZATION}/maintainers-highlight",
                "description": "Highlighted models"
            }
        ]
        
        # Analyze each dataset
        results = []
        for dataset in datasets:
            logger.info(f"\nAnalyzing {dataset['description']} ({dataset['id']})...")
            result = analyze_dataset(dataset['id'])
            results.append(result)
            
            if 'error' in result:
                logger.error(f"❌ Error: {result['error']}")
            else:
                logger.info(f"✓ {result['total_entries']} entries")
                logger.info(f"✓ {result['file_count']} files")
                logger.info(f"✓ {result['size_bytes'] / 1024:.1f} KB")
                logger.info(f"✓ {result['downloads']} downloads")
                
                if 'pending_requests' in result:
                    logger.info(f"✓ {result['pending_requests']} pending requests")
                    logger.info(f"✓ {result['completed_requests']} completed requests")
                
                if result['last_modified']:
                    last_modified = datetime.fromisoformat(result['last_modified'].replace('Z', '+00:00'))
                    logger.info(f"✓ Last modified: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results
            
    except Exception as e:
        logger.error(f"Global error: {str(e)}")
        return []

if __name__ == "__main__":
    main() 