from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path
import logging
import aiohttp
import asyncio
import time
from huggingface_hub import HfApi, CommitOperationAdd
from huggingface_hub.utils import build_hf_headers
from datasets import disable_progress_bar
import sys
import contextlib
from concurrent.futures import ThreadPoolExecutor
import tempfile

from app.config import (
    QUEUE_REPO,
    HF_TOKEN,
    EVAL_REQUESTS_PATH
)
from app.config.hf_config import HF_ORGANIZATION
from app.services.hf_service import HuggingFaceService
from app.utils.model_validation import ModelValidator
from app.services.votes import VoteService
from app.core.cache import cache_config
from app.utils.logging import LogFormatter

# Disable datasets progress bars globally
disable_progress_bar()

logger = logging.getLogger(__name__)

# Context manager to temporarily disable stdout and stderr
@contextlib.contextmanager
def suppress_output():
    stdout = sys.stdout
    stderr = sys.stderr
    devnull = open(os.devnull, 'w')
    try:
        sys.stdout = devnull
        sys.stderr = devnull
        yield
    finally:
        sys.stdout = stdout
        sys.stderr = stderr
        devnull.close()

class ProgressTracker:
    def __init__(self, total: int, desc: str = "Progress", update_frequency: int = 10):
        self.total = total
        self.current = 0
        self.desc = desc
        self.start_time = time.time()
        self.update_frequency = update_frequency  # Percentage steps
        self.last_update = -1
        
        # Initial log with fancy formatting
        logger.info(LogFormatter.section(desc))
        logger.info(LogFormatter.info(f"Starting processing of {total:,} items..."))
        sys.stdout.flush()
    
    def update(self, n: int = 1):
        self.current += n
        current_percentage = (self.current * 100) // self.total
        
        # Only update on frequency steps (e.g., 0%, 10%, 20%, etc.)
        if current_percentage >= self.last_update + self.update_frequency or current_percentage == 100:
            elapsed = time.time() - self.start_time
            rate = self.current / elapsed if elapsed > 0 else 0
            remaining = (self.total - self.current) / rate if rate > 0 else 0
            
            # Create progress stats
            stats = {
                "Progress": LogFormatter.progress_bar(self.current, self.total),
                "Items": f"{self.current:,}/{self.total:,}",
                "Time": f"⏱️  {elapsed:.1f}s elapsed, {remaining:.1f}s remaining",
                "Rate": f"🚀 {rate:.1f} items/s"
            }
            
            # Log progress using tree format
            for line in LogFormatter.tree(stats):
                logger.info(line)
            sys.stdout.flush()
            
            self.last_update = (current_percentage // self.update_frequency) * self.update_frequency
    
    def close(self):
        elapsed = time.time() - self.start_time
        rate = self.total / elapsed if elapsed > 0 else 0
        
        # Final summary with fancy formatting
        logger.info(LogFormatter.section("COMPLETED"))
        stats = {
            "Total": f"{self.total:,} items",
            "Time": f"{elapsed:.1f}s",
            "Rate": f"{rate:.1f} items/s"
        }
        for line in LogFormatter.stats(stats):
            logger.info(line)
        logger.info("="*50)
        sys.stdout.flush()

class ModelService(HuggingFaceService):
    _instance: Optional['ModelService'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            logger.info(LogFormatter.info("Creating new ModelService instance"))
            cls._instance = super(ModelService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_init_done'):
            logger.info(LogFormatter.section("MODEL SERVICE INITIALIZATION"))
            super().__init__()
            self.validator = ModelValidator()
            self.vote_service = VoteService()
            self.eval_requests_path = cache_config.eval_requests_file
            logger.info(LogFormatter.info(f"Using eval requests path: {self.eval_requests_path}"))
            
            self.eval_requests_path.parent.mkdir(parents=True, exist_ok=True)
            self.hf_api = HfApi(token=HF_TOKEN)
            self.cached_models = None
            self.last_cache_update = 0
            self.cache_ttl = cache_config.cache_ttl.total_seconds()
            self._init_done = True
            logger.info(LogFormatter.success("Initialization complete"))

    async def _download_and_process_file(self, file: str, session: aiohttp.ClientSession, progress: ProgressTracker) -> Optional[Dict]:
        """Download and process a file asynchronously"""
        try:
            # Build file URL
            url = f"https://huggingface.co/datasets/{QUEUE_REPO}/resolve/main/{file}"
            headers = build_hf_headers(token=self.token)
            
            # Download file
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(LogFormatter.error(f"Failed to download {file}", f"HTTP {response.status}"))
                    progress.update()
                    return None
                
                try:
                    # First read content as text
                    text_content = await response.text()
                    # Then parse JSON
                    content = json.loads(text_content)
                except json.JSONDecodeError as e:
                    logger.error(LogFormatter.error(f"Failed to decode JSON from {file}", e))
                    progress.update()
                    return None
                
            # Get status and determine target status
            status = content.get("status", "PENDING").upper()
            target_status = None
            status_map = {
                "PENDING": ["PENDING"],
                "EVALUATING": ["RUNNING"],
                "FINISHED": ["FINISHED"]
            }
            
            for target, source_statuses in status_map.items():
                if status in source_statuses:
                    target_status = target
                    break
                    
            if not target_status:
                progress.update()
                return None
                
            # Calculate wait time
            try:
                submit_time = datetime.fromisoformat(content["submitted_time"].replace("Z", "+00:00"))
                if submit_time.tzinfo is None:
                    submit_time = submit_time.replace(tzinfo=timezone.utc)
                current_time = datetime.now(timezone.utc)
                wait_time = current_time - submit_time
                
                model_info = {
                    "name": content["model"],
                    "submitter": content.get("sender", "Unknown"),
                    "revision": content["revision"],
                    "wait_time": f"{wait_time.total_seconds():.1f}s",
                    "submission_time": content["submitted_time"],
                    "status": target_status,
                    "precision": content.get("precision", "Unknown")
                }
                
                progress.update()
                return model_info
                    
            except (ValueError, TypeError) as e:
                logger.error(LogFormatter.error(f"Failed to process {file}", e))
                progress.update()
                return None
                
        except Exception as e:
            logger.error(LogFormatter.error(f"Failed to load {file}", e))
            progress.update()
            return None

    async def _refresh_models_cache(self):
        """Refresh the models cache"""
        try:
            logger.info(LogFormatter.section("CACHE REFRESH"))
            self._log_repo_operation("read", f"{HF_ORGANIZATION}/requests", "Refreshing models cache")
            
            # Initialize models dictionary
            models = {
                "finished": [],
                "evaluating": [],
                "pending": []
            }
            
            try:
                logger.info(LogFormatter.subsection("DATASET LOADING"))
                logger.info(LogFormatter.info("Loading dataset files..."))
                
                # List files in repository
                with suppress_output():
                    files = self.hf_api.list_repo_files(
                        repo_id=QUEUE_REPO,
                        repo_type="dataset",
                        token=self.token
                    )
                
                # Filter JSON files
                json_files = [f for f in files if f.endswith('.json')]
                total_files = len(json_files)
                
                # Log repository stats
                stats = {
                    "Total_Files": len(files),
                    "JSON_Files": total_files,
                }
                for line in LogFormatter.stats(stats, "Repository Statistics"):
                    logger.info(line)
                
                if not json_files:
                    raise Exception("No JSON files found in repository")
                
                # Initialize progress tracker
                progress = ProgressTracker(total_files, "PROCESSING FILES")
                
                try:
                    # Create aiohttp session to reuse connections
                    async with aiohttp.ClientSession() as session:
                        # Process files in chunks
                        chunk_size = 50
                        
                        for i in range(0, len(json_files), chunk_size):
                            chunk = json_files[i:i + chunk_size]
                            chunk_tasks = [
                                self._download_and_process_file(file, session, progress)
                                for file in chunk
                            ]
                            results = await asyncio.gather(*chunk_tasks)
                            
                            # Process results
                            for result in results:
                                if result:
                                    status = result.pop("status")
                                    models[status.lower()].append(result)
                
                finally:
                    progress.close()
                
                # Final summary with fancy formatting
                logger.info(LogFormatter.section("CACHE SUMMARY"))
                stats = {
                    "Finished": len(models["finished"]),
                    "Evaluating": len(models["evaluating"]),
                    "Pending": len(models["pending"])
                }
                for line in LogFormatter.stats(stats, "Models by Status"):
                    logger.info(line)
                logger.info("="*50)
                
            except Exception as e:
                logger.error(LogFormatter.error("Error processing files", e))
                raise
            
            # Update cache
            self.cached_models = models
            self.last_cache_update = time.time()
            logger.info(LogFormatter.success("Cache updated successfully"))
            
            return models
            
        except Exception as e:
            logger.error(LogFormatter.error("Cache refresh failed", e))
            raise

    async def initialize(self):
        """Initialize the model service"""
        if self._initialized:
            logger.info(LogFormatter.info("Service already initialized, using cached data"))
            return
        
        try:
            logger.info(LogFormatter.section("MODEL SERVICE INITIALIZATION"))
            
            # Check if cache already exists
            cache_path = cache_config.get_cache_path("datasets")
            if not cache_path.exists() or not any(cache_path.iterdir()):
                logger.info(LogFormatter.info("No existing cache found, initializing datasets cache..."))
                cache_config.flush_cache("datasets")
            else:
                logger.info(LogFormatter.info("Using existing datasets cache"))
            
            # Ensure eval requests directory exists
            self.eval_requests_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(LogFormatter.info(f"Eval requests directory: {self.eval_requests_path}"))
            
            # List existing files
            if self.eval_requests_path.exists():
                files = list(self.eval_requests_path.glob("**/*.json"))
                stats = {
                    "Total_Files": len(files),
                    "Directory": str(self.eval_requests_path)
                }
                for line in LogFormatter.stats(stats, "Eval Requests"):
                    logger.info(line)
            
            # Load initial cache
            await self._refresh_models_cache()
            
            self._initialized = True
            logger.info(LogFormatter.success("Model service initialization complete"))
            
        except Exception as e:
            logger.error(LogFormatter.error("Initialization failed", e))
            raise

    async def get_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all models with their status"""
        if not self._initialized:
            logger.info(LogFormatter.info("Service not initialized, initializing now..."))
            await self.initialize()
            
        current_time = time.time()
        cache_age = current_time - self.last_cache_update
        
        # Check if cache needs refresh
        if not self.cached_models:
            logger.info(LogFormatter.info("No cached data available, refreshing cache..."))
            return await self._refresh_models_cache()
        elif cache_age > self.cache_ttl:
            logger.info(LogFormatter.info(f"Cache expired ({cache_age:.1f}s old, TTL: {self.cache_ttl}s)"))
            return await self._refresh_models_cache()
        else:
            logger.info(LogFormatter.info(f"Using cached data ({cache_age:.1f}s old)"))
            return self.cached_models

    async def submit_model(
        self, 
        model_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        logger.info(LogFormatter.section("MODEL SUBMISSION"))
        self._log_repo_operation("write", f"{HF_ORGANIZATION}/requests", f"Submitting model {model_data['model_id']} by {user_id}")
        stats = {
            "Model": model_data["model_id"],
            "User": user_id,
            "Revision": model_data["revision"],
            "Precision": model_data["precision"],
            "Type": model_data["model_type"]
        }
        for line in LogFormatter.tree(stats, "Submission Details"):
            logger.info(line)
        
        # Validate required fields
        required_fields = [
            "model_id", "base_model", "revision", "precision",
            "weight_type", "model_type", "use_chat_template"
        ]
        for field in required_fields:
            if field not in model_data:
                raise ValueError(f"Missing required field: {field}")

        # Get model info and validate it exists on HuggingFace
        try:
            logger.info(LogFormatter.subsection("MODEL VALIDATION"))
            
            # Get the model info to check if it exists
            model_info = self.hf_api.model_info(
                model_data["model_id"],
                revision=model_data["revision"],
                token=self.token
            )
            
            if not model_info:
                raise Exception(f"Model {model_data['model_id']} not found on HuggingFace Hub")
            
            logger.info(LogFormatter.success("Model exists on HuggingFace Hub"))
            
        except Exception as e:
            logger.error(LogFormatter.error("Model validation failed", e))
            raise
        
        # Update model revision with commit sha
        model_data["revision"] = model_info.sha

        # Check if model already exists in the system
        try:
            logger.info(LogFormatter.subsection("CHECKING EXISTING SUBMISSIONS"))
            existing_models = await self.get_models()
            
            # Check in all statuses (pending, evaluating, finished)
            for status, models in existing_models.items():
                for model in models:
                    if model["name"] == model_data["model_id"] and model["revision"] == model_data["revision"]:
                        error_msg = f"Model {model_data['model_id']} revision {model_data['revision']} is already in the system with status: {status}"
                        logger.error(LogFormatter.error("Submission rejected", error_msg))
                        raise ValueError(error_msg)
            
            logger.info(LogFormatter.success("No existing submission found"))
        except ValueError:
            raise
        except Exception as e:
            logger.error(LogFormatter.error("Failed to check existing submissions", e))
            raise

        # Check that model on hub and valid
        valid, error, model_config = await self.validator.is_model_on_hub(
            model_data["model_id"], 
            model_data["revision"], 
            test_tokenizer=True
        )
        if not valid:
            logger.error(LogFormatter.error("Model on hub validation failed", error))
            raise Exception(error)
        logger.info(LogFormatter.success("Model on hub validation passed"))

        # Validate model card
        valid, error, model_card = await self.validator.check_model_card(
            model_data["model_id"]
        )
        if not valid:
            logger.error(LogFormatter.error("Model card validation failed", error))
            raise Exception(error)
        logger.info(LogFormatter.success("Model card validation passed"))

        # Check size limits
        model_size, error = await self.validator.get_model_size(
            model_info,
            model_data["precision"],
            model_data["base_model"],
            revision=model_data["revision"]
        )
        if model_size is None:
            logger.error(LogFormatter.error("Model size validation failed", error))
            raise Exception(error)
        logger.info(LogFormatter.success(f"Model size validation passed: {model_size:.1f}B"))

        # Size limits based on precision
        if model_data["precision"] in ["float16", "bfloat16"] and model_size > 100:
            error_msg = f"Model too large for {model_data['precision']} (limit: 100B)"
            logger.error(LogFormatter.error("Size limit exceeded", error_msg))
            raise Exception(error_msg)

        # Chat template validation if requested
        if model_data["use_chat_template"]:
            valid, error = await self.validator.check_chat_template(
                model_data["model_id"],
                model_data["revision"]
            )
            if not valid:
                logger.error(LogFormatter.error("Chat template validation failed", error))
                raise Exception(error)
            logger.info(LogFormatter.success("Chat template validation passed"))


        architectures = model_info.config.get("architectures", "")     
        if architectures:
            architectures = ";".join(architectures)

        # Create eval entry
        eval_entry = {
            "model": model_data["model_id"],
            "base_model": model_data["base_model"],
            "revision": model_info.sha,
            "precision": model_data["precision"],
            "params": model_size,
            "architectures": architectures,
            "weight_type": model_data["weight_type"],
            "status": "PENDING",
            "submitted_time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "model_type": model_data["model_type"],
            "job_id": -1,
            "job_start_time": None,
            "use_chat_template": model_data["use_chat_template"],
            "sender": user_id
        }
        
        logger.info(LogFormatter.subsection("EVALUATION ENTRY"))
        for line in LogFormatter.tree(eval_entry):
            logger.info(line)

        # Upload to HF dataset
        try:
            logger.info(LogFormatter.subsection("UPLOADING TO HUGGINGFACE"))
            logger.info(LogFormatter.info(f"Uploading to {HF_ORGANIZATION}/requests..."))
            
            # Construct the path in the dataset
            org_or_user = model_data["model_id"].split("/")[0] if "/" in model_data["model_id"] else ""
            model_path = model_data["model_id"].split("/")[-1]
            relative_path = f"{org_or_user}/{model_path}_eval_request_False_{model_data['precision']}_{model_data['weight_type']}.json"
            
            # Create a temporary file with the request
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(eval_entry, temp_file, indent=2)
                temp_file.flush()
                temp_path = temp_file.name
            
            # Upload file directly
            self.hf_api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo=relative_path,
                repo_id=f"{HF_ORGANIZATION}/requests",
                repo_type="dataset",
                commit_message=f"Add {model_data['model_id']} to eval queue",
                token=self.token
            )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            logger.info(LogFormatter.success("Upload successful"))
            
        except Exception as e:
            logger.error(LogFormatter.error("Upload failed", e))
            raise

        # Add automatic vote
        try:
            logger.info(LogFormatter.subsection("AUTOMATIC VOTE"))
            logger.info(LogFormatter.info(f"Adding upvote for {model_data['model_id']} by {user_id}"))
            await self.vote_service.add_vote(
                model_data["model_id"],
                user_id,
                "up"
            )
            logger.info(LogFormatter.success("Vote recorded successfully"))
        except Exception as e:
            logger.error(LogFormatter.error("Failed to record vote", e))
            # Don't raise here as the main submission was successful

        return {
            "status": "success",
            "message": "The model was submitted successfully, and the vote has been recorded"
        }

    async def get_model_status(self, model_id: str) -> Dict[str, Any]:
        """Get evaluation status of a model"""
        logger.info(LogFormatter.info(f"Checking status for model: {model_id}"))
        eval_path = self.eval_requests_path
        
        for user_folder in eval_path.iterdir():
            if user_folder.is_dir():
                for file in user_folder.glob("*.json"):
                    with open(file, "r") as f:
                        data = json.load(f)
                        if data["model"] == model_id:
                            status = {
                                "status": data["status"],
                                "submitted_time": data["submitted_time"],
                                "job_id": data.get("job_id", -1)
                            }
                            logger.info(LogFormatter.success("Status found"))
                            for line in LogFormatter.tree(status, "Model Status"):
                                logger.info(line)
                            return status
        
        logger.warning(LogFormatter.warning(f"No status found for model: {model_id}"))
        return {"status": "not_found"} 