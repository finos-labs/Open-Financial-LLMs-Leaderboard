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

    return set([file_name.lower().split("eval_requests/")[1] for file_name in file_names])

def load_all_info_from_hub(LMEH_REPO):
    auto_eval_repo = None
    requested_models = None
    if H4_TOKEN:
        print("Pulling evaluation requests and results.")

        auto_eval_repo = Repository(
            local_dir="./auto_evals/",
            clone_from=LMEH_REPO,
            use_auth_token=H4_TOKEN,
            repo_type="dataset",
        )
        auto_eval_repo.git_pull()

        requested_models_dir = "./auto_evals/eval_requests"
        requested_models = get_all_requested_models(requested_models_dir)

    return auto_eval_repo, requested_models


#def load_results(model, benchmark, metric):
#    file_path = os.path.join("autoevals", model, f"{model}-eval_{benchmark}.json")
#    if not os.path.exists(file_path):
#        return 0.0, None

#    with open(file_path) as fp:
#        data = json.load(fp)
#    accs = np.array([v[metric] for k, v in data["results"].items()])
#    mean_acc = np.mean(accs)
#    return mean_acc, data["config"]["model_args"]
