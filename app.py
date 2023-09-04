import json
import os
from datetime import datetime, timezone

import gradio as gr
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from huggingface_hub import HfApi

from src.assets.css_html_js import custom_css, get_window_url_params
from src.assets.text_content import (
    CITATION_BUTTON_LABEL,
    CITATION_BUTTON_TEXT,
    EVALUATION_QUEUE_TEXT,
    INTRODUCTION_TEXT,
    LLM_BENCHMARKS_TEXT,
    TITLE,
)
from src.display_models.get_model_metadata import DO_NOT_SUBMIT_MODELS, ModelType
from src.display_models.utils import (
    AutoEvalColumn,
    EvalQueueColumn,
    fields,
    styled_error,
    styled_message,
    styled_warning,
)
from src.load_from_hub import get_evaluation_queue_df, get_leaderboard_df, is_model_on_hub, load_all_info_from_hub

pd.set_option("display.precision", 1)

# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)

QUEUE_REPO = "open-llm-leaderboard/requests"
RESULTS_REPO = "open-llm-leaderboard/results"

PRIVATE_QUEUE_REPO = "open-llm-leaderboard/private-requests"
PRIVATE_RESULTS_REPO = "open-llm-leaderboard/private-results"

IS_PUBLIC = bool(os.environ.get("IS_PUBLIC", True))

EVAL_REQUESTS_PATH = "eval-queue"
EVAL_RESULTS_PATH = "eval-results"

EVAL_REQUESTS_PATH_PRIVATE = "eval-queue-private"
EVAL_RESULTS_PATH_PRIVATE = "eval-results-private"

api = HfApi(token=H4_TOKEN)


def restart_space():
    api.restart_space(repo_id="HuggingFaceH4/open_llm_leaderboard", token=H4_TOKEN)


# Column selection
COLS = [c.name for c in fields(AutoEvalColumn) if not c.hidden]
TYPES = [c.type for c in fields(AutoEvalColumn) if not c.hidden]
COLS_LITE = [c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.hidden]
TYPES_LITE = [c.type for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.hidden]

if not IS_PUBLIC:
    COLS.insert(2, AutoEvalColumn.precision.name)
    TYPES.insert(2, AutoEvalColumn.precision.type)

EVAL_COLS = [c.name for c in fields(EvalQueueColumn)]
EVAL_TYPES = [c.type for c in fields(EvalQueueColumn)]

BENCHMARK_COLS = [
    c.name
    for c in [
        AutoEvalColumn.arc,
        AutoEvalColumn.hellaswag,
        AutoEvalColumn.mmlu,
        AutoEvalColumn.truthfulqa,
    ]
]

## LOAD INFO FROM HUB
eval_queue, requested_models, eval_results = load_all_info_from_hub(
    QUEUE_REPO, RESULTS_REPO, EVAL_REQUESTS_PATH, EVAL_RESULTS_PATH
)

if not IS_PUBLIC:
    (eval_queue_private, requested_models_private, eval_results_private,) = load_all_info_from_hub(
        PRIVATE_QUEUE_REPO,
        PRIVATE_RESULTS_REPO,
        EVAL_REQUESTS_PATH_PRIVATE,
        EVAL_RESULTS_PATH_PRIVATE,
    )
else:
    eval_queue_private, eval_results_private = None, None

original_df = get_leaderboard_df(eval_results, eval_results_private, COLS, BENCHMARK_COLS)
models = original_df["model_name_for_query"].tolist() # needed for model backlinks in their to the leaderboard

leaderboard_df = original_df.copy()
(
    finished_eval_queue_df,
    running_eval_queue_df,
    pending_eval_queue_df,
) = get_evaluation_queue_df(eval_queue, eval_queue_private, EVAL_REQUESTS_PATH, EVAL_COLS)


## INTERACTION FUNCTIONS
def add_new_eval(
    model: str,
    base_model: str,
    revision: str,
    precision: str,
    private: bool,
    weight_type: str,
    model_type: str,
):
    precision = precision.split(" ")[0]
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if model_type is None or model_type == "":
        return styled_error("Please select a model type.")

    # check the model actually exists before adding the eval
    if revision == "":
        revision = "main"

    if weight_type in ["Delta", "Adapter"]:
        base_model_on_hub, error = is_model_on_hub(base_model, revision)
        if not base_model_on_hub:
            return styled_error(f'Base model "{base_model}" {error}')

    if not weight_type == "Adapter":
        model_on_hub, error = is_model_on_hub(model, revision)
        if not model_on_hub:
            return styled_error(f'Model "{model}" {error}')

    print("adding new eval")

    eval_entry = {
        "model": model,
        "base_model": base_model,
        "revision": revision,
        "private": private,
        "precision": precision,
        "weight_type": weight_type,
        "status": "PENDING",
        "submitted_time": current_time,
        "model_type": model_type,
    }

    user_name = ""
    model_path = model
    if "/" in model:
        user_name = model.split("/")[0]
        model_path = model.split("/")[1]

    OUT_DIR = f"{EVAL_REQUESTS_PATH}/{user_name}"
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/{model_path}_eval_request_{private}_{precision}_{weight_type}.json"

    # Check if the model has been forbidden:
    if out_path.split("eval-queue/")[1] in DO_NOT_SUBMIT_MODELS:
        return styled_warning("Model authors have requested that their model be not submitted on the leaderboard.")

    # Check for duplicate submission
    if f"{model}_{revision}_{precision}" in requested_models:
        return styled_warning("This model has been already submitted.")

    with open(out_path, "w") as f:
        f.write(json.dumps(eval_entry))

    api.upload_file(
        path_or_fileobj=out_path,
        path_in_repo=out_path.split("eval-queue/")[1],
        repo_id=QUEUE_REPO,
        repo_type="dataset",
        commit_message=f"Add {model} to eval queue",
    )

    # remove the local file
    os.remove(out_path)

    return styled_message(
        "Your request has been submitted to the evaluation queue!\nPlease wait for up to an hour for the model to show in the PENDING list."
    )


# Basics
def refresh() -> list[pd.DataFrame]:
    leaderboard_df = get_leaderboard_df(eval_results, eval_results_private, COLS, BENCHMARK_COLS)
    (
        finished_eval_queue_df,
        running_eval_queue_df,
        pending_eval_queue_df,
    ) = get_evaluation_queue_df(eval_queue, eval_queue_private, EVAL_REQUESTS_PATH, COLS)
    return (
        leaderboard_df,
        finished_eval_queue_df,
        running_eval_queue_df,
        pending_eval_queue_df,
    )


def change_tab(query_param: str):
    query_param = query_param.replace("'", '"')
    query_param = json.loads(query_param)

    if isinstance(query_param, dict) and "tab" in query_param and query_param["tab"] == "evaluation":
        return gr.Tabs.update(selected=1)
    else:
        return gr.Tabs.update(selected=0)


# Searching and filtering
def search_table(df: pd.DataFrame, current_columns_df: pd.DataFrame, query: str) -> pd.DataFrame:
    current_columns = current_columns_df.columns
    if AutoEvalColumn.model_type.name in current_columns:
        filtered_df = df[
            (df[AutoEvalColumn.dummy.name].str.contains(query, case=False))
            | (df[AutoEvalColumn.model_type.name].str.contains(query, case=False))
        ]
    else:
        filtered_df = df[(df[AutoEvalColumn.dummy.name].str.contains(query, case=False))]
    return filtered_df[current_columns]


def select_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    always_here_cols = [
        AutoEvalColumn.model_type_symbol.name,
        AutoEvalColumn.model.name,
    ]
    # We use COLS to maintain sorting
    filtered_df = df[
        always_here_cols + [c for c in COLS if c in df.columns and c in columns] + [AutoEvalColumn.dummy.name]
    ]
    return filtered_df

NUMERIC_INTERVALS = {
    "< 1.5B": (0, 1.5),
    "~3B": (1.5, 5),
    "~7B": (6, 11),
    "~13B": (12, 15),
    "~35B": (16, 55),
    "60B+": (55, 10000),
}

def filter_models(
    df: pd.DataFrame, current_columns_df: pd.DataFrame, type_query: list, size_query: list, show_deleted: bool
) -> pd.DataFrame:
    current_columns = current_columns_df.columns

    # Show all models
    if show_deleted:
        filtered_df = df[current_columns]
    else:  # Show only still on the hub models
        filtered_df = df[df[AutoEvalColumn.still_on_hub.name] == True][current_columns]

    type_emoji = [t[0] for t in type_query]
    filtered_df = filtered_df[df[AutoEvalColumn.model_type_symbol.name].isin(type_emoji)]

    numeric_interval = [NUMERIC_INTERVALS[s] for s in size_query]
    params_column = pd.to_numeric(df[AutoEvalColumn.params.name], errors="coerce")
    filtered_df = filtered_df[params_column.between(numeric_interval[0][0], numeric_interval[-1][1])]

    return filtered_df


demo = gr.Blocks(css=custom_css)
with demo:
    gr.HTML(TITLE)
    gr.Markdown(INTRODUCTION_TEXT, elem_classes="markdown-text")

    with gr.Tabs(elem_classes="tab-buttons") as tabs:
        with gr.TabItem("🏅 LLM Benchmark", elem_id="llm-benchmark-tab-table", id=0):
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        shown_columns = gr.CheckboxGroup(
                            choices=[
                                c
                                for c in COLS
                                if c
                                not in [
                                    AutoEvalColumn.dummy.name,
                                    AutoEvalColumn.model.name,
                                    AutoEvalColumn.model_type_symbol.name,
                                    AutoEvalColumn.still_on_hub.name,
                                ]
                            ],
                            value=[
                                c
                                for c in COLS_LITE
                                if c
                                not in [
                                    AutoEvalColumn.dummy.name,
                                    AutoEvalColumn.model.name,
                                    AutoEvalColumn.model_type_symbol.name,
                                    AutoEvalColumn.still_on_hub.name,
                                ]
                            ],
                            label="Select columns to show",
                            elem_id="column-select",
                            interactive=True,
                        )
                    with gr.Row():
                        deleted_models_visibility = gr.Checkbox(
                            value=True, label="Show models removed from the hub", interactive=True
                        )
                with gr.Column(min_width=320):
                    search_bar = gr.Textbox(
                        placeholder="🔍 Search for your model and press ENTER...",
                        show_label=False,
                        elem_id="search-bar",
                    )
                    with gr.Box(elem_id="box-filter"):
                        filter_columns_type = gr.CheckboxGroup(
                            label="Model types",
                            choices=[
                                ModelType.PT.to_str(),
                                ModelType.FT.to_str(),
                                ModelType.IFT.to_str(),
                                ModelType.RL.to_str(),
                            ],
                            value=[
                                ModelType.PT.to_str(),
                                ModelType.FT.to_str(),
                                ModelType.IFT.to_str(),
                                ModelType.RL.to_str(),
                            ],
                            interactive=True,
                            elem_id="filter-columns-type",
                        )
                        filter_columns_size = gr.CheckboxGroup(
                            label="Model sizes",
                            choices=list(NUMERIC_INTERVALS.keys()),
                            value=list(NUMERIC_INTERVALS.keys()),
                            interactive=True,
                            elem_id="filter-columns-size",
                        )

            leaderboard_table = gr.components.Dataframe(
                value=leaderboard_df[
                    [AutoEvalColumn.model_type_symbol.name, AutoEvalColumn.model.name]
                    + shown_columns.value
                    + [AutoEvalColumn.dummy.name]
                ],
                headers=[
                    AutoEvalColumn.model_type_symbol.name,
                    AutoEvalColumn.model.name,
                ]
                + shown_columns.value
                + [AutoEvalColumn.dummy.name],
                datatype=TYPES,
                max_rows=None,
                elem_id="leaderboard-table",
                interactive=False,
                visible=True,
            )

            # Dummy leaderboard for handling the case when the user uses backspace key
            hidden_leaderboard_table_for_search = gr.components.Dataframe(
                value=original_df,
                headers=COLS,
                datatype=TYPES,
                max_rows=None,
                visible=False,
            )
            search_bar.submit(
                search_table,
                [
                    hidden_leaderboard_table_for_search,
                    leaderboard_table,
                    search_bar,
                ],
                leaderboard_table,
            )
            shown_columns.change(
                select_columns,
                [hidden_leaderboard_table_for_search, shown_columns],
                leaderboard_table,
                queue=False,
            )
            filter_columns_type.change(
                filter_models,
                [
                    hidden_leaderboard_table_for_search,
                    leaderboard_table,
                    filter_columns_type,
                    filter_columns_size,
                    deleted_models_visibility,
                ],
                leaderboard_table,
                queue=False,
            )
            filter_columns_size.change(
                filter_models,
                [
                    hidden_leaderboard_table_for_search,
                    leaderboard_table,
                    filter_columns_type,
                    filter_columns_size,
                    deleted_models_visibility,
                ],
                leaderboard_table,
                queue=False,
            )
            deleted_models_visibility.change(
                filter_models,
                [
                    hidden_leaderboard_table_for_search,
                    leaderboard_table,
                    filter_columns_type,
                    filter_columns_size,
                    deleted_models_visibility,
                ],
                leaderboard_table,
                queue=False,
            )
        with gr.TabItem("📝 About", elem_id="llm-benchmark-tab-table", id=2):
            gr.Markdown(LLM_BENCHMARKS_TEXT, elem_classes="markdown-text")

        with gr.TabItem("🚀 Submit here! ", elem_id="llm-benchmark-tab-table", id=3):
            with gr.Column():
                with gr.Row():
                    gr.Markdown(EVALUATION_QUEUE_TEXT, elem_classes="markdown-text")

                with gr.Column():
                    with gr.Accordion(
                        f"✅ Finished Evaluations ({len(finished_eval_queue_df)})",
                        open=False,
                    ):
                        with gr.Row():
                            finished_eval_table = gr.components.Dataframe(
                                value=finished_eval_queue_df,
                                headers=EVAL_COLS,
                                datatype=EVAL_TYPES,
                                max_rows=5,
                            )
                    with gr.Accordion(
                        f"🔄 Running Evaluation Queue ({len(running_eval_queue_df)})",
                        open=False,
                    ):
                        with gr.Row():
                            running_eval_table = gr.components.Dataframe(
                                value=running_eval_queue_df,
                                headers=EVAL_COLS,
                                datatype=EVAL_TYPES,
                                max_rows=5,
                            )

                    with gr.Accordion(
                        f"⏳ Pending Evaluation Queue ({len(pending_eval_queue_df)})",
                        open=False,
                    ):
                        with gr.Row():
                            pending_eval_table = gr.components.Dataframe(
                                value=pending_eval_queue_df,
                                headers=EVAL_COLS,
                                datatype=EVAL_TYPES,
                                max_rows=5,
                            )
            with gr.Row():
                gr.Markdown("# ✉️✨ Submit your model here!", elem_classes="markdown-text")

            with gr.Row():
                with gr.Column():
                    model_name_textbox = gr.Textbox(label="Model name")
                    revision_name_textbox = gr.Textbox(label="revision", placeholder="main")
                    private = gr.Checkbox(False, label="Private", visible=not IS_PUBLIC)
                    model_type = gr.Dropdown(
                        choices=[
                            ModelType.PT.to_str(" : "),
                            ModelType.FT.to_str(" : "),
                            ModelType.IFT.to_str(" : "),
                            ModelType.RL.to_str(" : "),
                        ],
                        label="Model type",
                        multiselect=False,
                        value=None,
                        interactive=True,
                    )

                with gr.Column():
                    precision = gr.Dropdown(
                        choices=[
                            "float16",
                            "bfloat16",
                            "8bit (LLM.int8)",
                            "4bit (QLoRA / FP4)",
                            "GPTQ"
                        ],
                        label="Precision",
                        multiselect=False,
                        value="float16",
                        interactive=True,
                    )
                    weight_type = gr.Dropdown(
                        choices=["Original", "Delta", "Adapter"],
                        label="Weights type",
                        multiselect=False,
                        value="Original",
                        interactive=True,
                    )
                    base_model_name_textbox = gr.Textbox(label="Base model (for delta or adapter weights)")

            submit_button = gr.Button("Submit Eval")
            submission_result = gr.Markdown()
            submit_button.click(
                add_new_eval,
                [
                    model_name_textbox,
                    base_model_name_textbox,
                    revision_name_textbox,
                    precision,
                    private,
                    weight_type,
                    model_type,
                ],
                submission_result,
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

    with gr.Row():
        with gr.Accordion("📙 Citation", open=False):
            citation_button = gr.Textbox(
                value=CITATION_BUTTON_TEXT,
                label=CITATION_BUTTON_LABEL,
                elem_id="citation-button",
            ).style(show_copy_button=True)

    dummy = gr.Textbox(visible=False)
    demo.load(
        change_tab,
        dummy,
        tabs,
        _js=get_window_url_params,
    )

scheduler = BackgroundScheduler()
scheduler.add_job(restart_space, "interval", seconds=3600)
scheduler.start()
demo.queue(concurrency_count=40).launch()
