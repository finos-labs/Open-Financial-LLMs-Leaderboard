import os
import shutil
import tempfile
import logging
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download, upload_folder, create_repo
from dotenv import load_dotenv

# Configure source and destination usernames
SOURCE_USERNAME = "TheFinAI"
DESTINATION_USERNAME = "tfrere"

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

# List of dataset names to sync
DATASET_NAMES = [
    "votes",
    "results",
    "requests",
    "greek-contents",
    "maintainers-highlight",
]

# Build list of datasets with their source and destination paths
DATASETS = [
    (name, f"{SOURCE_USERNAME}/{name}", f"{DESTINATION_USERNAME}/{name}")
    for name in DATASET_NAMES
]

# Initialize Hugging Face API
api = HfApi()

def ensure_repo_exists(repo_id, token):
    """Ensure the repository exists, create it if it doesn't"""
    try:
        api.repo_info(repo_id=repo_id, repo_type="dataset")
        logger.info(f"✓ Repository {repo_id} already exists")
    except Exception:
        logger.info(f"Creating repository {repo_id}...")
        create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            token=token,
            private=True
        )
        logger.info(f"✓ Repository {repo_id} created")

def process_dataset(dataset_info, token):
    """Process a single dataset"""
    name, source_dataset, destination_dataset = dataset_info
    try:
        logger.info(f"\n📥 Processing dataset: {name}")
        
        # Ensure destination repository exists
        ensure_repo_exists(destination_dataset, token)
        
        # Create a temporary directory for this dataset
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # List files in source dataset
                logger.info(f"Listing files in {source_dataset}...")
                files = api.list_repo_files(source_dataset, repo_type="dataset")
                logger.info(f"Detected structure: {len(files)} files")
                
                # Download dataset
                logger.info(f"Downloading from {source_dataset}...")
                local_dir = snapshot_download(
                    repo_id=source_dataset,
                    repo_type="dataset",
                    local_dir=temp_dir,
                    token=token
                )
                logger.info(f"✓ Download complete")
                
                # Upload to destination while preserving structure
                logger.info(f"📤 Uploading to {destination_dataset}...")
                api.upload_folder(
                    folder_path=local_dir,
                    repo_id=destination_dataset,
                    repo_type="dataset",
                    token=token
                )
                logger.info(f"✅ {name} copied successfully!")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error processing {name}: {str(e)}")
                return False

    except Exception as e:
        logger.error(f"❌ Error for {name}: {str(e)}")
        return False

def copy_datasets():
    try:
        logger.info("🔑 Checking authentication...")
        # Get token from .env file
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN not found in .env file")
        
        # Process datasets sequentially
        results = []
        for dataset_info in DATASETS:
            success = process_dataset(dataset_info, token)
            results.append((dataset_info[0], success))
            
        # Print final summary
        logger.info("\n📊 Final summary:")
        for dataset, success in results:
            status = "✅ Success" if success else "❌ Failure"
            logger.info(f"{dataset}: {status}")
            
    except Exception as e:
        logger.error(f"❌ Global error: {str(e)}")

if __name__ == "__main__":
    copy_datasets() 
