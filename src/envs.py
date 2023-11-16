import os

from huggingface_hub import HfApi

# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)

REPO_ID = "HuggingFaceH4/open_llm_leaderboard"
QUEUE_REPO = "open-llm-leaderboard/requests"
RESULTS_REPO = "open-llm-leaderboard/results"

PRIVATE_QUEUE_REPO = "open-llm-leaderboard/private-requests"
PRIVATE_RESULTS_REPO = "open-llm-leaderboard/private-results"

IS_PUBLIC = bool(os.environ.get("IS_PUBLIC", True))

CACHE_PATH=os.getenv("HF_HOME", ".")

EVAL_REQUESTS_PATH = os.path.join(CACHE_PATH, "eval-queue")
EVAL_RESULTS_PATH = os.path.join(CACHE_PATH, "eval-results")

EVAL_REQUESTS_PATH_PRIVATE = "eval-queue-private"
EVAL_RESULTS_PATH_PRIVATE = "eval-results-private"

PATH_TO_COLLECTION = "open-llm-leaderboard/llm-leaderboard-best-models-652d6c7965a4619fb5c27a03"

# Rate limit variables
RATE_LIMIT_PERIOD = 7
RATE_LIMIT_QUOTA = 5
HAS_HIGHER_RATE_LIMIT = ["TheBloke"]

API = HfApi(token=H4_TOKEN)
