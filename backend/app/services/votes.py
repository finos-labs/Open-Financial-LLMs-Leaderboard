from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Tuple, Optional
import json
import logging
import asyncio
from pathlib import Path
import os
import aiohttp
from huggingface_hub import HfApi
import datasets

from app.services.hf_service import HuggingFaceService
from app.config import HF_TOKEN, API
from app.config.hf_config import HF_ORGANIZATION
from app.core.cache import cache_config
from app.utils.logging import LogFormatter

logger = logging.getLogger(__name__)

class VoteService(HuggingFaceService):
    _instance: Optional['VoteService'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoteService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_init_done'):
            super().__init__()
            self.votes_file = cache_config.votes_file
            self.votes_to_upload: List[Dict[str, Any]] = []
            self.vote_check_set: Set[Tuple[str, str, str]] = set()
            self._votes_by_model: Dict[str, List[Dict[str, Any]]] = {}
            self._votes_by_user: Dict[str, List[Dict[str, Any]]] = {}
            self._upload_lock = asyncio.Lock()
            self._last_sync = None
            self._sync_interval = 300  # 5 minutes
            self._total_votes = 0
            self._last_vote_timestamp = None
            self._max_retries = 3
            self._retry_delay = 1  # seconds
            self._upload_batch_size = 10
            self.hf_api = HfApi(token=HF_TOKEN)
            self._init_done = True

    async def initialize(self):
        """Initialize the vote service"""
        if self._initialized:
            await self._check_for_new_votes()
            return
        
        try:
            logger.info(LogFormatter.section("VOTE SERVICE INITIALIZATION"))
            
            # Ensure votes directory exists
            self.votes_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing votes if file exists
            local_vote_count = 0
            if self.votes_file.exists():
                logger.info(LogFormatter.info(f"Loading votes from {self.votes_file}"))
                local_vote_count = await self._count_local_votes()
                logger.info(LogFormatter.info(f"Found {local_vote_count:,} local votes"))
            
            # Check remote votes count
            remote_vote_count = await self._count_remote_votes()
            logger.info(LogFormatter.info(f"Found {remote_vote_count:,} remote votes"))
            
            if remote_vote_count > local_vote_count:
                logger.info(LogFormatter.info(f"Fetching {remote_vote_count - local_vote_count:,} new votes"))
                await self._sync_with_hub()
            elif remote_vote_count < local_vote_count:
                logger.warning(LogFormatter.warning(f"Local votes ({local_vote_count:,}) > Remote votes ({remote_vote_count:,})"))
                await self._load_existing_votes()
            else:
                logger.info(LogFormatter.success("Local and remote votes are in sync"))
                if local_vote_count > 0:
                    await self._load_existing_votes()
                else:
                    logger.info(LogFormatter.info("No votes found"))
            
            self._initialized = True
            self._last_sync = datetime.now(timezone.utc)
            
            # Final summary
            stats = {
                "Total_Votes": self._total_votes,
                "Last_Sync": self._last_sync.strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            logger.info(LogFormatter.section("INITIALIZATION COMPLETE"))
            for line in LogFormatter.stats(stats):
                logger.info(line)
            
        except Exception as e:
            logger.error(LogFormatter.error("Initialization failed", e))
            raise

    async def _count_local_votes(self) -> int:
        """Count votes in local file"""
        if not self.votes_file.exists():
            return 0
            
        count = 0
        try:
            with open(self.votes_file, 'r') as f:
                for _ in f:
                    count += 1
            return count
        except Exception as e:
            logger.error(f"Error counting local votes: {str(e)}")
            return 0

    async def _count_remote_votes(self) -> int:
        """Count votes in remote file"""
        url = f"https://huggingface.co/datasets/{HF_ORGANIZATION}/votes/raw/main/votes_data.jsonl"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        count = 0
                        async for line in response.content:
                            if line.strip():  # Skip empty lines
                                count += 1
                        return count
                    else:
                        logger.error(f"Failed to get remote votes: HTTP {response.status}")
                        return 0
        except Exception as e:
            logger.error(f"Error counting remote votes: {str(e)}")
            return 0

    async def _sync_with_hub(self):
        """Sync votes with HuggingFace hub using datasets"""
        try:
            logger.info(LogFormatter.section("VOTE SYNC"))
            self._log_repo_operation("sync", f"{HF_ORGANIZATION}/votes", "Syncing local votes with HF hub")
            logger.info(LogFormatter.info("Syncing with HuggingFace hub..."))
            
            # Load votes from HF dataset
            dataset = datasets.load_dataset(
                f"{HF_ORGANIZATION}/votes", 
                split="train",
                cache_dir=cache_config.get_cache_path("datasets")
            )
            
            remote_votes = len(dataset)
            logger.info(LogFormatter.info(f"Dataset loaded with {remote_votes:,} votes"))
            
            # Convert to list of dictionaries
            df = dataset.to_pandas()
            if 'timestamp' in df.columns:
                df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            remote_votes = df.to_dict('records')
            
            # If we have more remote votes than local
            if len(remote_votes) > self._total_votes:
                new_votes = len(remote_votes) - self._total_votes
                logger.info(LogFormatter.info(f"Processing {new_votes:,} new votes..."))
                
                # Save votes to local file
                with open(self.votes_file, 'w') as f:
                    for vote in remote_votes:
                        f.write(json.dumps(vote) + '\n')
                
                # Reload votes in memory
                await self._load_existing_votes()
                logger.info(LogFormatter.success("Sync completed successfully"))
            else:
                logger.info(LogFormatter.success("Local votes are up to date"))

            self._last_sync = datetime.now(timezone.utc)
            
        except Exception as e:
            logger.error(LogFormatter.error("Sync failed", e))
            raise

    async def _check_for_new_votes(self):
        """Check for new votes on the hub"""
        try:
            self._log_repo_operation("check", f"{HF_ORGANIZATION}/votes", "Checking for new votes")
            # Load only dataset metadata
            dataset_info = datasets.load_dataset(f"{HF_ORGANIZATION}/votes", split="train")
            remote_vote_count = len(dataset_info)
            
            if remote_vote_count > self._total_votes:
                logger.info(f"Found {remote_vote_count - self._total_votes} new votes on hub")
                await self._sync_with_hub()
            else:
                logger.info("No new votes found on hub")
                
        except Exception as e:
            logger.error(f"Error checking for new votes: {str(e)}")

    async def _load_existing_votes(self):
        """Load existing votes from file"""
        if not self.votes_file.exists():
            logger.warning(LogFormatter.warning("No votes file found"))
            return

        try:
            logger.info(LogFormatter.section("LOADING VOTES"))
            
            # Clear existing data structures
            self.vote_check_set.clear()
            self._votes_by_model.clear()
            self._votes_by_user.clear()
            
            vote_count = 0
            latest_timestamp = None
            
            with open(self.votes_file, "r") as f:
                for line in f:
                    try:
                        vote = json.loads(line.strip())
                        vote_count += 1
                        
                        # Track latest timestamp
                        try:
                            vote_timestamp = datetime.fromisoformat(vote["timestamp"].replace("Z", "+00:00"))
                            if not latest_timestamp or vote_timestamp > latest_timestamp:
                                latest_timestamp = vote_timestamp
                            vote["timestamp"] = vote_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                        except (KeyError, ValueError) as e:
                            logger.warning(LogFormatter.warning(f"Invalid timestamp in vote: {str(e)}"))
                            continue
                        
                        if vote_count % 1000 == 0:
                            logger.info(LogFormatter.info(f"Processed {vote_count:,} votes..."))
                        
                        self._add_vote_to_memory(vote)
                        
                    except json.JSONDecodeError as e:
                        logger.error(LogFormatter.error("Vote parsing failed", e))
                        continue
                    except Exception as e:
                        logger.error(LogFormatter.error("Vote processing failed", e))
                        continue
            
            self._total_votes = vote_count
            self._last_vote_timestamp = latest_timestamp
            
            # Final summary
            stats = {
                "Total_Votes": vote_count,
                "Latest_Vote": latest_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if latest_timestamp else "None",
                "Unique_Models": len(self._votes_by_model),
                "Unique_Users": len(self._votes_by_user)
            }
            
            logger.info(LogFormatter.section("VOTE SUMMARY"))
            for line in LogFormatter.stats(stats):
                logger.info(line)
            
        except Exception as e:
            logger.error(LogFormatter.error("Failed to load votes", e))
            raise

    def _add_vote_to_memory(self, vote: Dict[str, Any]):
        """Add vote to memory structures"""
        try:
            check_tuple = (vote["model"], vote["revision"], vote["username"])
            
            # Skip if we already have this vote
            if check_tuple in self.vote_check_set:
                return
                
            self.vote_check_set.add(check_tuple)
            
            # Update model votes
            if vote["model"] not in self._votes_by_model:
                self._votes_by_model[vote["model"]] = []
            self._votes_by_model[vote["model"]].append(vote)
            
            # Update user votes
            if vote["username"] not in self._votes_by_user:
                self._votes_by_user[vote["username"]] = []
            self._votes_by_user[vote["username"]].append(vote)
            
        except KeyError as e:
            logger.error(f"Malformed vote data, missing key: {str(e)}")
        except Exception as e:
            logger.error(f"Error adding vote to memory: {str(e)}")

    async def get_user_votes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all votes from a specific user"""
        logger.info(LogFormatter.info(f"Fetching votes for user: {user_id}"))
        votes = self._votes_by_user.get(user_id, [])
        logger.info(LogFormatter.success(f"Found {len(votes):,} votes"))
        return votes

    async def get_model_votes(self, model_id: str) -> Dict[str, Any]:
        """Get all votes for a specific model"""
        logger.info(LogFormatter.info(f"Fetching votes for model: {model_id}"))
        votes = self._votes_by_model.get(model_id, [])
        
        # Group votes by revision
        votes_by_revision = {}
        for vote in votes:
            revision = vote["revision"]
            if revision not in votes_by_revision:
                votes_by_revision[revision] = 0
            votes_by_revision[revision] += 1
        
        stats = {
            "Total_Votes": len(votes),
            **{f"Revision_{k}": v for k, v in votes_by_revision.items()}
        }
        
        logger.info(LogFormatter.section("VOTE STATISTICS"))
        for line in LogFormatter.stats(stats):
            logger.info(line)
        
        return {
            "total_votes": len(votes),
            "votes_by_revision": votes_by_revision,
            "votes": votes
        }

    async def _get_model_revision(self, model_id: str) -> str:
        """Get current revision of a model with retries"""
        logger.info(f"Getting revision for model: {model_id}")
        for attempt in range(self._max_retries):
            try:
                model_info = await asyncio.to_thread(self.hf_api.model_info, model_id)
                logger.info(f"Successfully got revision {model_info.sha} for model {model_id}")
                return model_info.sha
            except Exception as e:
                logger.error(f"Error getting model revision for {model_id} (attempt {attempt + 1}): {str(e)}")
                if attempt < self._max_retries - 1:
                    retry_delay = self._retry_delay * (attempt + 1)
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.warning(f"Using 'main' as fallback revision for {model_id} after {self._max_retries} failed attempts")
                    return "main"

    async def add_vote(self, model_id: str, user_id: str, vote_type: str) -> Dict[str, Any]:
        """Add a vote for a model"""
        try:
            self._log_repo_operation("add", f"{HF_ORGANIZATION}/votes", f"Adding {vote_type} vote for {model_id} by {user_id}")
            logger.info(LogFormatter.section("NEW VOTE"))
            stats = {
                "Model": model_id,
                "User": user_id,
                "Type": vote_type
            }
            for line in LogFormatter.tree(stats, "Vote Details"):
                logger.info(line)
            
            revision = await self._get_model_revision(model_id)
            check_tuple = (model_id, revision, user_id)
            
            if check_tuple in self.vote_check_set:
                raise ValueError("Vote already recorded for this model")

            vote = {
                "model": model_id,
                "revision": revision,
                "username": user_id,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "vote_type": vote_type
            }

            # Update local storage
            with open(self.votes_file, "a") as f:
                f.write(json.dumps(vote) + "\n")
            
            self._add_vote_to_memory(vote)
            self.votes_to_upload.append(vote)
            
            stats = {
                "Status": "Success",
                "Queue_Size": len(self.votes_to_upload)
            }
            for line in LogFormatter.stats(stats):
                logger.info(line)
            
            # Try to upload if batch size reached
            if len(self.votes_to_upload) >= self._upload_batch_size:
                logger.info(LogFormatter.info(f"Upload batch size reached ({self._upload_batch_size}), triggering sync"))
                await self._sync_with_hub()
            
            return {"status": "success", "message": "Vote added successfully"}
            
        except Exception as e:
            logger.error(LogFormatter.error("Failed to add vote", e))
            raise