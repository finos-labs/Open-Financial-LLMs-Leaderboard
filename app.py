import json
import os
from datetime import datetime, timezone

import gradio as gr
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from huggingface_hub import HfApi, snapshot_download

from src.assets.css_html_js import custom_css, get_window_url_params
from src.assets.text_content import (
    CITATION_BUTTON_LABEL,
    CITATION_BUTTON_TEXT,
    EVALUATION_QUEUE_TEXT,
    INTRODUCTION_TEXT,
    LLM_BENCHMARKS_TEXT,
    TITLE,
)
from src.plots.plot_results import (
    create_metric_plot_obj,
    create_scores_df,
    create_plot_df,
    join_model_info_with_results,
    HUMAN_BASELINES,
)
from src.get_model_info.apply_metadata_to_df import DO_NOT_SUBMIT_MODELS, ModelType
from src.get_model_info.get_metadata_from_hub import get_model_size
from src.filters import check_model_card
from src.get_model_info.utils import (
    AutoEvalColumn,
    EvalQueueColumn,
    fields,
    styled_error,
    styled_message,
    styled_warning,
)
from src.manage_collections import update_collections
from src.load_from_hub import get_all_requested_models, get_evaluation_queue_df, get_leaderboard_df
from src.filters import is_model_on_hub, user_submission_permission

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


# Rate limit variables
RATE_LIMIT_PERIOD = 7
RATE_LIMIT_QUOTA = 5

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
        AutoEvalColumn.winogrande,
        AutoEvalColumn.gsm8k,
        AutoEvalColumn.drop
    ]
]

try:
    snapshot_download(repo_id=QUEUE_REPO, local_dir=EVAL_REQUESTS_PATH, repo_type="dataset", tqdm_class=None, etag_timeout=30)
except Exception:
    restart_space()
try:
    snapshot_download(repo_id=RESULTS_REPO, local_dir=EVAL_RESULTS_PATH, repo_type="dataset", tqdm_class=None, etag_timeout=30)
except Exception:
    restart_space()

requested_models, users_to_submission_dates = get_all_requested_models(EVAL_REQUESTS_PATH)

original_df = get_leaderboard_df(EVAL_RESULTS_PATH, COLS, BENCHMARK_COLS)
update_collections(original_df.copy())
leaderboard_df = original_df.copy()

models = original_df["model_name_for_query"].tolist()  # needed for model backlinks in their to the leaderboard
#plot_df = create_plot_df(create_scores_df(join_model_info_with_results(original_df)))
to_be_dumped = f"models = {repr(models)}\n"

(
    finished_eval_queue_df,
    running_eval_queue_df,
    pending_eval_queue_df,
) = get_evaluation_queue_df(EVAL_REQUESTS_PATH, EVAL_COLS)


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

    # Is the user rate limited?
    user_can_submit, error_msg = user_submission_permission(model, users_to_submission_dates, RATE_LIMIT_PERIOD, RATE_LIMIT_QUOTA)
    if not user_can_submit:
        return styled_error(error_msg)

    # Did the model authors forbid its submission to the leaderboard?
    if model in DO_NOT_SUBMIT_MODELS or base_model in DO_NOT_SUBMIT_MODELS:
        return styled_warning("Model authors have requested that their model be not submitted on the leaderboard.")

    # Does the model actually exist?
    if revision == "":
        revision = "main"

    if weight_type in ["Delta", "Adapter"]:
        base_model_on_hub, error = is_model_on_hub(base_model, revision, H4_TOKEN)
        if not base_model_on_hub:
            return styled_error(f'Base model "{base_model}" {error}')

    if not weight_type == "Adapter":
        model_on_hub, error = is_model_on_hub(model, revision)
        if not model_on_hub:
            return styled_error(f'Model "{model}" {error}')

    try:
        model_info = api.model_info(repo_id=model, revision=revision)
    except Exception:
        return styled_error("Could not get your model information. Please fill it up properly.")

    model_size = get_model_size(model_info=model_info , precision= precision)

    # Were the model card and license filled?
    try:
        license = model_info.cardData["license"]
    except Exception:
        return styled_error("Please select a license for your model")

    modelcard_OK, error_msg = check_model_card(model)
    if not modelcard_OK:
        return styled_error(error_msg)

    # Seems good, creating the eval
    print("Adding new eval")

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
        "likes": model_info.likes,
        "params": model_size,
        "license": license,
    }

    user_name = ""
    model_path = model
    if "/" in model:
        user_name = model.split("/")[0]
        model_path = model.split("/")[1]

    print("Creating eval file")
    OUT_DIR = f"{EVAL_REQUESTS_PATH}/{user_name}"
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/{model_path}_eval_request_{private}_{precision}_{weight_type}.json"

    # Check for duplicate submission
    if f"{model}_{revision}_{precision}" in requested_models:
        return styled_warning("This model has been already submitted.")

    with open(out_path, "w") as f:
        f.write(json.dumps(eval_entry))

    print("Uploading eval file")
    api.upload_file(
        path_or_fileobj=out_path,
        path_in_repo=out_path.split("eval-queue/")[1],
        repo_id=QUEUE_REPO,
        repo_type="dataset",
        commit_message=f"Add {model} to eval queue",
    )

    # Remove the local file
    os.remove(out_path)

    return styled_message(
        "Your request has been submitted to the evaluation queue!\nPlease wait for up to an hour for the model to show in the PENDING list."
    )


# Basics
def change_tab(query_param: str):
    query_param = query_param.replace("'", '"')
    query_param = json.loads(query_param)

    if isinstance(query_param, dict) and "tab" in query_param and query_param["tab"] == "evaluation":
        return gr.Tabs.update(selected=1)
    else:
        return gr.Tabs.update(selected=0)


# Searching and filtering
def update_table(
    hidden_df: pd.DataFrame,
    columns: list,
    type_query: list,
    precision_query: str,
    size_query: list,
    show_deleted: bool,
    query: str,
):
    filtered_df = filter_models(hidden_df, type_query, size_query, precision_query, show_deleted)
    filtered_df = filter_queries(query, filtered_df)
    df = select_columns(filtered_df, columns)
    return df


def search_table(df: pd.DataFrame, query: str) -> pd.DataFrame:
    return df[(df[AutoEvalColumn.dummy.name].str.contains(query, case=False))]


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
    "?": pd.Interval(-1, 0, closed="right"),
    "~1.5": pd.Interval(0, 2, closed="right"),
    "~3": pd.Interval(2, 4, closed="right"),
    "~7": pd.Interval(4, 9, closed="right"),
    "~13": pd.Interval(9, 20, closed="right"),
    "~35": pd.Interval(20, 45, closed="right"),
    "~60": pd.Interval(45, 70, closed="right"),
    "70+": pd.Interval(70, 10000, closed="right"),
}


def filter_queries(query: str, filtered_df: pd.DataFrame):
    """Added by Abishek"""
    final_df = []
    if query != "":
        queries = [q.strip() for q in query.split(";")]
        for _q in queries:
            _q = _q.strip()
            if _q != "":
                temp_filtered_df = search_table(filtered_df, _q)
                if len(temp_filtered_df) > 0:
                    final_df.append(temp_filtered_df)
        if len(final_df) > 0:
            filtered_df = pd.concat(final_df)
            filtered_df = filtered_df.drop_duplicates(
                subset=[AutoEvalColumn.model.name, AutoEvalColumn.precision.name, AutoEvalColumn.revision.name]
            )

    return filtered_df


def filter_models(
    df: pd.DataFrame, type_query: list, size_query: list, precision_query: list, show_deleted: bool
) -> pd.DataFrame:
    # Show all models
    if show_deleted:
        filtered_df = df
    else:  # Show only still on the hub models
        filtered_df = df[df[AutoEvalColumn.still_on_hub.name] is True]

    type_emoji = [t[0] for t in type_query]
    filtered_df = filtered_df[df[AutoEvalColumn.model_type_symbol.name].isin(type_emoji)]
    filtered_df = filtered_df[df[AutoEvalColumn.precision.name].isin(precision_query + ["None"])]

    numeric_interval = pd.IntervalIndex(sorted([NUMERIC_INTERVALS[s] for s in size_query]))
    params_column = pd.to_numeric(df[AutoEvalColumn.params.name], errors="coerce")
    mask = params_column.apply(lambda x: any(numeric_interval.contains(x)))
    filtered_df = filtered_df.loc[mask]

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
                        search_bar = gr.Textbox(
                            placeholder=" 🔍 Search for your model (separate multiple queries with `;`) and press ENTER...",
                            show_label=False,
                            elem_id="search-bar",
                        )
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
                            value=True, label="Show gated/private/deleted models", interactive=True
                        )
                with gr.Column(min_width=320):
                    with gr.Box(elem_id="box-filter"):
                        filter_columns_type = gr.CheckboxGroup(
                            label="Model types",
                            choices=[
                                ModelType.PT.to_str(),
                                ModelType.FT.to_str(),
                                ModelType.IFT.to_str(),
                                ModelType.RL.to_str(),
                                ModelType.Unknown.to_str(),
                            ],
                            value=[
                                ModelType.PT.to_str(),
                                ModelType.FT.to_str(),
                                ModelType.IFT.to_str(),
                                ModelType.RL.to_str(),
                                ModelType.Unknown.to_str(),
                            ],
                            interactive=True,
                            elem_id="filter-columns-type",
                        )
                        filter_columns_precision = gr.CheckboxGroup(
                            label="Precision",
                            choices=["torch.float16", "torch.bfloat16", "torch.float32", "8bit", "4bit", "GPTQ"],
                            value=["torch.float16", "torch.bfloat16", "torch.float32", "8bit", "4bit", "GPTQ"],
                            interactive=True,
                            elem_id="filter-columns-precision",
                        )
                        filter_columns_size = gr.CheckboxGroup(
                            label="Model sizes (in billions of parameters)",
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
                update_table,
                [
                    hidden_leaderboard_table_for_search,
                    shown_columns,
                    filter_columns_type,
                    filter_columns_precision,
                    filter_columns_size,
                    deleted_models_visibility,
                    search_bar,
                ],
                leaderboard_table,
            )
            shown_columns.change(
                update_table,
                [
                    hidden_leaderboard_table_for_search,
                    shown_columns,
                    filter_columns_type,
                    filter_columns_precision,
                    filter_columns_size,
                    deleted_models_visibility,
                    search_bar,
                ],
                leaderboard_table,
                queue=True,
            )
            filter_columns_type.change(
                update_table,
                [
                    hidden_leaderboard_table_for_search,
                    shown_columns,
                    filter_columns_type,
                    filter_columns_precision,
                    filter_columns_size,
                    deleted_models_visibility,
                    search_bar,
                ],
                leaderboard_table,
                queue=True,
            )
            filter_columns_precision.change(
                update_table,
                [
                    hidden_leaderboard_table_for_search,
                    shown_columns,
                    filter_columns_type,
                    filter_columns_precision,
                    filter_columns_size,
                    deleted_models_visibility,
                    search_bar,
                ],
                leaderboard_table,
                queue=True,
            )
            filter_columns_size.change(
                update_table,
                [
                    hidden_leaderboard_table_for_search,
                    shown_columns,
                    filter_columns_type,
                    filter_columns_precision,
                    filter_columns_size,
                    deleted_models_visibility,
                    search_bar,
                ],
                leaderboard_table,
                queue=True,
            )
            deleted_models_visibility.change(
                update_table,
                [
                    hidden_leaderboard_table_for_search,
                    shown_columns,
                    filter_columns_type,
                    filter_columns_precision,
                    filter_columns_size,
                    deleted_models_visibility,
                    search_bar,
                ],
                leaderboard_table,
                queue=True,
            )

        # with gr.TabItem("📈 Metrics evolution through time", elem_id="llm-benchmark-tab-table", id=4):
        #     with gr.Row():
        #         with gr.Column():
        #             chart = create_metric_plot_obj(
        #                 plot_df,
        #                 ["Average ⬆️"],
        #                 HUMAN_BASELINES,
        #                 title="Average of Top Scores and Human Baseline Over Time",
        #             )
        #             gr.Plot(value=chart, interactive=False, width=500, height=500)
        #         with gr.Column():
        #             chart = create_metric_plot_obj(
        #                 plot_df,
        #                 ["ARC", "HellaSwag", "MMLU", "TruthfulQA", "Winogrande", "GSM8K", "DROP"],
        #                 HUMAN_BASELINES,
        #                 title="Top Scores and Human Baseline Over Time",
        #             )
        #             gr.Plot(value=chart, interactive=False, width=500, height=500)
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
                        choices=["float16", "bfloat16", "8bit (LLM.int8)", "4bit (QLoRA / FP4)", "GPTQ"],
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
        with gr.Accordion("📙 Citation", open=False):
            citation_button = gr.Textbox(
                value=CITATION_BUTTON_TEXT,
                label=CITATION_BUTTON_LABEL,
                lines=20,
                elem_id="citation-button",
                show_copy_button=True,
            )

    dummy = gr.Textbox(visible=False)
    demo.load(
        change_tab,
        dummy,
        tabs,
        _js=get_window_url_params,
    )

scheduler = BackgroundScheduler()
scheduler.add_job(restart_space, "interval", seconds=1800)
scheduler.start()
demo.queue(concurrency_count=40).launch()
