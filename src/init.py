import os 
from huggingface_hub import Repository

H4_TOKEN = os.environ.get("H4_TOKEN", None)


def get_all_requested_models(requested_models_dir):
    depth = 1
    file_names = []

    for root, dirs, files in os.walk(requested_models_dir):
        current_depth = root.count(os.sep) - requested_models_dir.count(os.sep)
        if current_depth == depth:
            file_names.extend([os.path.join(root, file) for file in files])

    return set([file_name.lower().split("eval-queue/")[1] for file_name in file_names])

def load_all_info_from_hub(QUEUE_REPO, RESULTS_REPO, QUEUE_PATH, RESULTS_PATH):
    eval_queue_repo = None
    eval_results_repo = None
    requested_models = None

    if H4_TOKEN:
        print("Pulling evaluation requests and results.")

        eval_queue_repo = Repository(
            local_dir=QUEUE_PATH,
            clone_from=QUEUE_REPO,
            use_auth_token=H4_TOKEN,
            repo_type="dataset",
        )
        eval_queue_repo.git_pull()

        eval_results_repo = Repository(
            local_dir=RESULTS_PATH,
            clone_from=RESULTS_REPO,
            use_auth_token=H4_TOKEN,
            repo_type="dataset",
        )
        eval_results_repo.git_pull()

        requested_models = get_all_requested_models("eval-queue")
    else:
        print("No HuggingFace token provided. Skipping evaluation requests and results.")

    return eval_queue_repo, requested_models, eval_results_repo


#def load_results(model, benchmark, metric):
#    file_path = os.path.join("autoevals", model, f"{model}-eval_{benchmark}.json")
#    if not os.path.exists(file_path):
#        return 0.0, None

#    with open(file_path) as fp:
#        data = json.load(fp)
#    accs = np.array([v[metric] for k, v in data["results"].items()])
#    mean_acc = np.mean(accs)
#    return mean_acc, data["config"]["model_args"]
