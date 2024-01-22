import logging
import pprint

from huggingface_hub import snapshot_download

logging.getLogger("openai").setLevel(logging.WARNING)

from src.backend.run_eval_suite import run_evaluation
from src.backend.manage_requests import check_completed_evals, get_eval_requests, set_eval_request
from src.backend.sort_queue import sort_models_by_priority

from src.envs import QUEUE_REPO, EVAL_REQUESTS_PATH_BACKEND, RESULTS_REPO, EVAL_RESULTS_PATH_BACKEND, DEVICE, API, LIMIT, TOKEN
from src.about import Tasks, NUM_FEWSHOT
TASKS_HARNESS = [task.value.benchmark for task in Tasks]

logging.basicConfig(level=logging.ERROR)
pp = pprint.PrettyPrinter(width=80)

PENDING_STATUS = "PENDING"
RUNNING_STATUS = "RUNNING"
FINISHED_STATUS = "FINISHED"
FAILED_STATUS = "FAILED"

snapshot_download(repo_id=RESULTS_REPO, revision="main", local_dir=EVAL_RESULTS_PATH_BACKEND, repo_type="dataset", max_workers=60, token=TOKEN)
snapshot_download(repo_id=QUEUE_REPO, revision="main", local_dir=EVAL_REQUESTS_PATH_BACKEND, repo_type="dataset", max_workers=60, token=TOKEN)

def run_auto_eval():
    current_pending_status = [PENDING_STATUS]

    # pull the eval dataset from the hub and parse any eval requests
    # check completed evals and set them to finished
    check_completed_evals(
        api=API,
        checked_status=RUNNING_STATUS,
        completed_status=FINISHED_STATUS,
        failed_status=FAILED_STATUS,
        hf_repo=QUEUE_REPO,
        local_dir=EVAL_REQUESTS_PATH_BACKEND,
        hf_repo_results=RESULTS_REPO,
        local_dir_results=EVAL_RESULTS_PATH_BACKEND
    )

    # Get all eval request that are PENDING, if you want to run other evals, change this parameter
    eval_requests = get_eval_requests(job_status=current_pending_status, hf_repo=QUEUE_REPO, local_dir=EVAL_REQUESTS_PATH_BACKEND)
    # Sort the evals by priority (first submitted first run)
    eval_requests = sort_models_by_priority(api=API, models=eval_requests)

    print(f"Found {len(eval_requests)} {','.join(current_pending_status)} eval requests")

    if len(eval_requests) == 0:
        return

    eval_request = eval_requests[0]
    pp.pprint(eval_request)

    set_eval_request(
        api=API,
        eval_request=eval_request,
        set_to_status=RUNNING_STATUS,
        hf_repo=QUEUE_REPO,
        local_dir=EVAL_REQUESTS_PATH_BACKEND,
    )

    run_evaluation(
        eval_request=eval_request, 
        task_names=TASKS_HARNESS, 
        num_fewshot=NUM_FEWSHOT, 
        local_dir=EVAL_RESULTS_PATH_BACKEND,
        results_repo=RESULTS_REPO,
        batch_size=1, 
        device=DEVICE, 
        no_cache=True, 
        limit=LIMIT
        )


if __name__ == "__main__":
    run_auto_eval()