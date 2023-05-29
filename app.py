import os
import json

import numpy as np
import gradio as gr
import pandas as pd

from apscheduler.schedulers.background import BackgroundScheduler
from content import *
from huggingface_hub import Repository, HfApi
from transformers import AutoConfig
from utils import get_eval_results_dicts, make_clickable_model

# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)
LMEH_REPO = "HuggingFaceH4/lmeh_evaluations"
IS_PUBLIC = bool(os.environ.get("IS_PUBLIC", None))

api = HfApi()
def restart_space():
    api.restart_space(repo_id="HuggingFaceH4/open_llm_leaderboard", token=H4_TOKEN)


def get_all_requested_models(requested_models_dir):
    depth = 1
    file_names = []

    for root, dirs, files in os.walk(requested_models_dir):
        current_depth = root.count(os.sep) - requested_models_dir.count(os.sep)
        if current_depth == depth:
            file_names.extend([os.path.join(root, file) for file in files])

    return set([file_name.lower().split("./evals/")[1] for file_name in file_names])

repo = None
requested_models = None
if H4_TOKEN:
    print("pulling repo")
    # try:
    #     shutil.rmtree("./evals/")
    # except:
    #     pass

    repo = Repository(
        local_dir="./evals/",
        clone_from=LMEH_REPO,
        use_auth_token=H4_TOKEN,
        repo_type="dataset",
    )
    repo.git_pull()

    requested_models_dir = "./evals/eval_requests"
    requested_models = get_all_requested_models(requested_models_dir)


# parse the results
BENCHMARKS = ["arc_challenge", "hellaswag", "hendrycks", "truthfulqa_mc"]
METRICS = ["acc_norm", "acc_norm", "acc_norm", "mc2"]


def load_results(model, benchmark, metric):
    file_path = os.path.join("evals", model, f"{model}-eval_{benchmark}.json")
    if not os.path.exists(file_path):
        return 0.0, None

    with open(file_path) as fp:
        data = json.load(fp)
    accs = np.array([v[metric] for k, v in data["results"].items()])
    mean_acc = np.mean(accs)
    return mean_acc, data["config"]["model_args"]


COLS = [
    "Model",
    "Revision",
    "Average ⬆️",
    "ARC (25-shot) ⬆️",
    "HellaSwag (10-shot) ⬆️",
    "MMLU (5-shot) ⬆️",
    "TruthfulQA (0-shot) ⬆️",
]
TYPES = [
    "markdown",
    "str",
    "number",
    "number",
    "number",
    "number",
    "number",
]

if not IS_PUBLIC:
    COLS.insert(2, "8bit")
    TYPES.insert(2, "bool")

EVAL_COLS = ["model", "revision", "private", "8bit_eval", "is_delta_weight", "status"]
EVAL_TYPES = ["markdown", "str", "bool", "bool", "bool", "str"]

BENCHMARK_COLS = [
    "ARC (25-shot) ⬆️",
    "HellaSwag (10-shot) ⬆️",
    "MMLU (5-shot) ⬆️",
    "TruthfulQA (0-shot) ⬆️",
]


def has_no_nan_values(df, columns):
    return df[columns].notna().all(axis=1)


def has_nan_values(df, columns):
    return df[columns].isna().any(axis=1)

def get_leaderboard():
    if repo:
        print("pulling changes")
        repo.git_pull()

    all_data = get_eval_results_dicts(IS_PUBLIC)

    if not IS_PUBLIC:
        gpt4_values = {
            "Model": f'<a target="_blank" href=https://arxiv.org/abs/2303.08774 style="color: var(--link-text-color); text-decoration: underline;text-decoration-style: dotted;">gpt4</a>',
            "Revision": "tech report",
            "8bit": None,
            "Average ⬆️": 84.3,
            "ARC (25-shot) ⬆️": 96.3,
            "HellaSwag (10-shot) ⬆️": 95.3,
            "MMLU (5-shot) ⬆️": 86.4,
            "TruthfulQA (0-shot) ⬆️": 59.0,
        }
        all_data.append(gpt4_values)
        gpt35_values = {
            "Model": f'<a target="_blank" href=https://arxiv.org/abs/2303.08774 style="color: var(--link-text-color); text-decoration: underline;text-decoration-style: dotted;">gpt3.5</a>',
            "Revision": "tech report",
            "8bit": None,
            "Average ⬆️": 71.9,
            "ARC (25-shot) ⬆️": 85.2,
            "HellaSwag (10-shot) ⬆️": 85.5,
            "MMLU (5-shot) ⬆️": 70.0,
            "TruthfulQA (0-shot) ⬆️": 47.0,
        }
        all_data.append(gpt35_values)

    base_line = {
        "Model": "<p>Baseline</p>",
        "Revision": "N/A",
        "8bit": None,
        "Average ⬆️": 25.0,
        "ARC (25-shot) ⬆️": 25.0,
        "HellaSwag (10-shot) ⬆️": 25.0,
        "MMLU (5-shot) ⬆️": 25.0,
        "TruthfulQA (0-shot) ⬆️": 25.0,
    }

    all_data.append(base_line)

    df = pd.DataFrame.from_records(all_data)
    df = df.sort_values(by=["Average ⬆️"], ascending=False)
    df = df[COLS]

    # get incomplete models
    incomplete_models = df[has_nan_values(df, BENCHMARK_COLS)]["Model"].tolist()
    print(
        [
            model.split(" style")[0].split("https://huggingface.co/")[1]
            for model in incomplete_models
        ]
    )

    # filter out if any of the benchmarks have not been produced
    df = df[has_no_nan_values(df, BENCHMARK_COLS)]
    return df


def get_eval_table():
    if repo:
        print("pulling changes for eval")
        repo.git_pull()
    entries = [
        entry
        for entry in os.listdir("evals/eval_requests")
        if not entry.startswith(".")
    ]
    all_evals = []

    for entry in entries:
        if ".json" in entry:
            file_path = os.path.join("evals/eval_requests", entry)
            with open(file_path) as fp:
                data = json.load(fp)

            data["# params"] = "unknown"
            data["model"] = make_clickable_model(data["model"])
            data["revision"] = data.get("revision", "main")

            all_evals.append(data)
        else:
            # this is a folder
            sub_entries = [
                e
                for e in os.listdir(f"evals/eval_requests/{entry}")
                if not e.startswith(".")
            ]
            for sub_entry in sub_entries:
                file_path = os.path.join("evals/eval_requests", entry, sub_entry)
                with open(file_path) as fp:
                    data = json.load(fp)

                # data["# params"] = get_n_params(data["model"])
                data["model"] = make_clickable_model(data["model"])
                all_evals.append(data)

    pending_list = [e for e in all_evals if e["status"] == "PENDING"]
    running_list = [e for e in all_evals if e["status"] == "RUNNING"]
    finished_list = [e for e in all_evals if e["status"] == "FINISHED"]
    df_pending = pd.DataFrame.from_records(pending_list)
    df_running = pd.DataFrame.from_records(running_list)
    df_finished = pd.DataFrame.from_records(finished_list)
    return df_finished[EVAL_COLS], df_running[EVAL_COLS], df_pending[EVAL_COLS]


leaderboard = get_leaderboard()
finished_eval_queue, running_eval_queue, pending_eval_queue = get_eval_table()


def is_model_on_hub(model_name, revision) -> bool:
    try:
        config = AutoConfig.from_pretrained(model_name, revision=revision)
        return True

    except Exception as e:
        print("Could not get the model config from the hub")
        print(e)
        return False


def add_new_eval(
    model: str,
    base_model: str,
    revision: str,
    is_8_bit_eval: bool,
    private: bool,
    is_delta_weight: bool,
):
    # check the model actually exists before adding the eval
    if revision == "":
        revision = "main"
    if is_delta_weight and not is_model_on_hub(base_model, revision):
        error_message = f'Base model "{base_model}" was not found on hub!'
        print(error_message)
        return f"<p style='color: red; font-size: 20px; text-align: center;'>{error_message}</p>"

    if not is_model_on_hub(model, revision):
        error_message = f'Model "{model}"was not found on hub!'
        return f"<p style='color: red; font-size: 20px; text-align: center;'>{error_message}</p>"

    print("adding new eval")

    eval_entry = {
        "model": model,
        "base_model": base_model,
        "revision": revision,
        "private": private,
        "8bit_eval": is_8_bit_eval,
        "is_delta_weight": is_delta_weight,
        "status": "PENDING",
    }

    user_name = ""
    model_path = model
    if "/" in model:
        user_name = model.split("/")[0]
        model_path = model.split("/")[1]

    OUT_DIR = f"eval_requests/{user_name}"
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/{model_path}_eval_request_{private}_{is_8_bit_eval}_{is_delta_weight}.json"

    # Check for duplicate submission
    if out_path.lower() in requested_models:
        duplicate_request_message = "This model has been already submitted."
        return f"<p style='color: orange; font-size: 20px; text-align: center;'>{duplicate_request_message}</p>"

    with open(out_path, "w") as f:
        f.write(json.dumps(eval_entry))
    LMEH_REPO = "HuggingFaceH4/lmeh_evaluations"

    api.upload_file(
        path_or_fileobj=out_path,
        path_in_repo=out_path,
        repo_id=LMEH_REPO,
        token=H4_TOKEN,
        repo_type="dataset",
    )

    success_message = "Your request has been submitted to the evaluation queue!"
    return f"<p style='color: green; font-size: 20px; text-align: center;'>{success_message}</p>"


def refresh():
    leaderboard = get_leaderboard()
    finished_eval_queue, running_eval_queue, pending_eval_queue = get_eval_table()
    return leaderboard, finished_eval_queue, running_eval_queue, pending_eval_queue

custom_css = """
#changelog-text {
    font-size: 18px !important;
}

.markdown-text {
    font-size: 16px !important;
}
"""

demo = gr.Blocks(css=custom_css)
with demo:
    gr.HTML(TITLE)
    with gr.Row():
        gr.Markdown(INTRODUCTION_TEXT, elem_classes="markdown-text")

    with gr.Accordion("CHANGELOG", open=False):
        changelog = gr.Markdown(CHANGELOG_TEXT, elem_id="changelog-text")

    with gr.Row():
        leaderboard_table = gr.components.Dataframe(
            value=leaderboard, headers=COLS, datatype=TYPES, max_rows=5
        )

    with gr.Row():
        gr.Markdown(EVALUATION_QUEUE_TEXT, elem_classes="markdown-text")

    with gr.Accordion("✅ Finished Evaluations", open=False):
        with gr.Row():
            finished_eval_table = gr.components.Dataframe(
                value=finished_eval_queue,
                headers=EVAL_COLS,
                datatype=EVAL_TYPES,
                max_rows=5,
            )
    with gr.Accordion("🔄 Running Evaluation Queue", open=False):
        with gr.Row():
            running_eval_table = gr.components.Dataframe(
                value=running_eval_queue,
                headers=EVAL_COLS,
                datatype=EVAL_TYPES,
                max_rows=5,
            )

    with gr.Accordion("⏳ Pending Evaluation Queue", open=False):
        with gr.Row():
            pending_eval_table = gr.components.Dataframe(
                value=pending_eval_queue,
                headers=EVAL_COLS,
                datatype=EVAL_TYPES,
                max_rows=5,
            )

    with gr.Row():
        refresh_button = gr.Button("Refresh")
        refresh_button.click(
            refresh,
            inputs=[],
            outputs=[
                leaderboard_table,
                finished_eval_table,
                running_eval_table,
                pending_eval_table,
            ],
        )

    with gr.Accordion("Submit a new model for evaluation"):
        with gr.Row():
            with gr.Column():
                model_name_textbox = gr.Textbox(label="Model name")
                revision_name_textbox = gr.Textbox(label="revision", placeholder="main")

            with gr.Column():
                is_8bit_toggle = gr.Checkbox(
                    False, label="8 bit eval", visible=not IS_PUBLIC
                )
                private = gr.Checkbox(False, label="Private", visible=not IS_PUBLIC)
                is_delta_weight = gr.Checkbox(False, label="Delta weights")
                base_model_name_textbox = gr.Textbox(label="base model (for delta)")

        with gr.Row():
            submit_button = gr.Button("Submit Eval")

        with gr.Row():
            submission_result = gr.Markdown()
            submit_button.click(
                add_new_eval,
                [
                    model_name_textbox,
                    base_model_name_textbox,
                    revision_name_textbox,
                    is_8bit_toggle,
                    private,
                    is_delta_weight,
                ],
                submission_result,
            )

scheduler = BackgroundScheduler()
scheduler.add_job(restart_space, 'interval', seconds=3600)
scheduler.start()
demo.launch()
