import os
import json
import pytz
import logging
import asyncio
from datetime import datetime
from pathlib import Path
import huggingface_hub
from huggingface_hub.errors import RepositoryNotFoundError, RevisionNotFoundError
from dotenv import load_dotenv
from git import Repo
from datetime import datetime
from tqdm.auto import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from app.config.hf_config import HF_TOKEN, QUEUE_REPO, API, EVAL_REQUESTS_PATH

from app.utils.model_validation import ModelValidator

huggingface_hub.logging.set_verbosity_error()
huggingface_hub.utils.disable_progress_bars()

logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()

validator = ModelValidator()

def get_changed_files(repo_path, start_date, end_date):
    repo = Repo(repo_path)
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    changed_files = set()
    pbar = tqdm(repo.iter_commits(), desc=f"Reading commits from {end_date} to {start_date}")
    for commit in pbar:
        commit_date = datetime.fromtimestamp(commit.committed_date)
        pbar.set_postfix_str(f"Commit date: {commit_date}")
        if start <= commit_date <= end:
            changed_files.update(item.a_path for item in commit.diff(commit.parents[0]))

        if commit_date < start:
            break

    return changed_files


def read_json(repo_path, file):
    with open(f"{repo_path}/{file}") as file:
        return json.load(file)


def write_json(repo_path, file, content):
    with open(f"{repo_path}/{file}", "w") as file:
        json.dump(content, file, indent=2)


def main():
    requests_path = "/Users/lozowski/Developer/requests"
    start_date = "2024-12-09"
    end_date = "2025-01-07"
  
    changed_files = get_changed_files(requests_path, start_date, end_date)

    for file in tqdm(changed_files):
        try:
            request_data = read_json(requests_path, file)
        except FileNotFoundError as e:
            tqdm.write(f"File {file} not found")
            continue
    
        try:
            model_info = API.model_info(
                repo_id=request_data["model"],
                revision=request_data["revision"],
                token=HF_TOKEN
            )
        except (RepositoryNotFoundError, RevisionNotFoundError) as e:
            tqdm.write(f"Model info for {request_data["model"]} not found")
            continue
        
        with logging_redirect_tqdm():
            new_model_size, error = asyncio.run(validator.get_model_size(
                model_info=model_info,
                precision=request_data["precision"],
                base_model=request_data["base_model"],
                revision=request_data["revision"]
            ))

        if error:
            tqdm.write(f"Error getting model size info for {request_data["model"]}, {error}")
            continue
        
        old_model_size = request_data["params"]
        if old_model_size != new_model_size:
            if new_model_size > 100:
                tqdm.write(f"Model: {request_data["model"]}, size is more 100B: {new_model_size}")
            
            tqdm.write(f"Model: {request_data["model"]}, old size: {request_data["params"]} new size: {new_model_size}")
            tqdm.write(f"Updating request file {file}")

            request_data["params"] = new_model_size
            write_json(requests_path, file, content=request_data)


if __name__ == "__main__":
    main()
