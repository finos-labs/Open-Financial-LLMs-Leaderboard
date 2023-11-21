import os

from huggingface_hub import HfApi

# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)

OWNER = "clefourrier"
REPO_ID = f"{OWNER}/leaderboard"
QUEUE_REPO = f"{OWNER}/requests"
RESULTS_REPO = f"{OWNER}/results"

CACHE_PATH=os.getenv("HF_HOME", ".")

# Local caches
EVAL_REQUESTS_PATH = os.path.join(CACHE_PATH, "eval-queue")
EVAL_RESULTS_PATH = os.path.join(CACHE_PATH, "eval-results")

API = HfApi(token=H4_TOKEN)
