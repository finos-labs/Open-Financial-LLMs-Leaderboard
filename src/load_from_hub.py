import json
import os

import pandas as pd
from huggingface_hub import Repository
from transformers import AutoConfig

from src.assets.hardcoded_evals import baseline, gpt4_values, gpt35_values
from src.display_models.get_model_metadata import apply_metadata
from src.display_models.read_results import get_eval_results_dicts, make_clickable_model
from src.display_models.utils import AutoEvalColumn, EvalQueueColumn, has_no_nan_values

IS_PUBLIC = bool(os.environ.get("IS_PUBLIC", True))


def get_all_requested_models(requested_models_dir: str) -> set[str]:
    depth = 1
    file_names = []

    for root, _, files in os.walk(requested_models_dir):
        current_depth = root.count(os.sep) - requested_models_dir.count(os.sep)
        if current_depth == depth:
            file_names.extend([os.path.join(root, file) for file in files])

    return set([file_name.lower().split("eval-queue/")[1] for file_name in file_names])


def load_all_info_from_hub(QUEUE_REPO: str, RESULTS_REPO: str, QUEUE_PATH: str, RESULTS_PATH: str) -> list[Repository]:
    eval_queue_repo = None
    eval_results_repo = None
    requested_models = None

    print("Pulling evaluation requests and results.")

    eval_queue_repo = Repository(
        local_dir=QUEUE_PATH,
        clone_from=QUEUE_REPO,
        repo_type="dataset",
    )
    eval_queue_repo.git_pull()

    eval_results_repo = Repository(
        local_dir=RESULTS_PATH,
        clone_from=RESULTS_REPO,
        repo_type="dataset",
    )
    eval_results_repo.git_pull()

    requested_models = get_all_requested_models("eval-queue")

    return eval_queue_repo, requested_models, eval_results_repo


def get_leaderboard_df(
    eval_results: Repository, eval_results_private: Repository, cols: list, benchmark_cols: list
) -> pd.DataFrame:
    if eval_results:
        print("Pulling evaluation results for the leaderboard.")
        eval_results.git_pull()
    if eval_results_private:
        print("Pulling evaluation results for the leaderboard.")
        eval_results_private.git_pull()

    all_data = get_eval_results_dicts()

    if not IS_PUBLIC:
        all_data.append(gpt4_values)
        all_data.append(gpt35_values)

    all_data.append(baseline)
    apply_metadata(all_data)  # Populate model type based on known hardcoded values in `metadata.py`

    df = pd.DataFrame.from_records(all_data)
    df = df.sort_values(by=[AutoEvalColumn.average.name], ascending=False)
    df = df[cols].round(decimals=2)

    # filter out if any of the benchmarks have not been produced
    df = df[has_no_nan_values(df, benchmark_cols)]
    return df


def get_evaluation_queue_df(
    eval_queue: Repository, eval_queue_private: Repository, save_path: str, cols: list
) -> list[pd.DataFrame]:
    if eval_queue:
        print("Pulling changes for the evaluation queue.")
        eval_queue.git_pull()
    if eval_queue_private:
        print("Pulling changes for the evaluation queue.")
        eval_queue_private.git_pull()

    entries = [entry for entry in os.listdir(save_path) if not entry.startswith(".")]
    all_evals = []

    for entry in entries:
        if ".json" in entry:
            file_path = os.path.join(save_path, entry)
            with open(file_path) as fp:
                data = json.load(fp)

            data[EvalQueueColumn.model.name] = make_clickable_model(data["model"])
            data[EvalQueueColumn.revision.name] = data.get("revision", "main")

            all_evals.append(data)
        elif ".md" not in entry:
            # this is a folder
            sub_entries = [e for e in os.listdir(f"{save_path}/{entry}") if not e.startswith(".")]
            for sub_entry in sub_entries:
                file_path = os.path.join(save_path, entry, sub_entry)
                with open(file_path) as fp:
                    data = json.load(fp)

                data[EvalQueueColumn.model.name] = make_clickable_model(data["model"])
                data[EvalQueueColumn.revision.name] = data.get("revision", "main")
                all_evals.append(data)

    pending_list = [e for e in all_evals if e["status"] in ["PENDING", "RERUN"]]
    running_list = [e for e in all_evals if e["status"] == "RUNNING"]
    finished_list = [e for e in all_evals if e["status"].startswith("FINISHED")]
    df_pending = pd.DataFrame.from_records(pending_list, columns=cols)
    df_running = pd.DataFrame.from_records(running_list, columns=cols)
    df_finished = pd.DataFrame.from_records(finished_list, columns=cols)
    return df_finished[cols], df_running[cols], df_pending[cols]


def is_model_on_hub(model_name: str, revision: str) -> bool:
    try:
        AutoConfig.from_pretrained(model_name, revision=revision, trust_remote_code=False)
        return True, None

    except ValueError:
        return (
            False,
            "needs to be launched with `trust_remote_code=True`. For safety reason, we do not allow these models to be automatically submitted to the leaderboard.",
        )

    except Exception as e:
        print(f"Could not get the model config from the hub.: {e}")
        return False, "was not found on hub!"
