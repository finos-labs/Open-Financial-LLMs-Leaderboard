import subprocess
import gradio as gr
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from huggingface_hub import snapshot_download
import os

from src.about import (
    CITATION_BUTTON_LABEL,
    CITATION_BUTTON_TEXT,
    EVALUATION_QUEUE_TEXT,
    INTRODUCTION_TEXT,
    LLM_BENCHMARKS_TEXT,
    TITLE,
)
from src.display.css_html_js import custom_css
from src.display.utils import (
    BENCHMARK_COLS,
    COLS,
    EVAL_COLS,
    EVAL_TYPES,
    NUMERIC_INTERVALS,
    TYPES,
    AutoEvalColumn,
    ModelType,
    fields,
    WeightType,
    Precision
)
from src.envs import API, EVAL_REQUESTS_PATH, EVAL_RESULTS_PATH, QUEUE_REPO, REPO_ID, RESULTS_REPO, TOKEN
from src.populate import get_evaluation_queue_df, get_leaderboard_df
from src.submission.submit import add_new_eval


def restart_space():
    API.restart_space(repo_id=REPO_ID)

try:
    print(EVAL_REQUESTS_PATH)
    snapshot_download(
        repo_id=QUEUE_REPO, local_dir=EVAL_REQUESTS_PATH, repo_type="dataset", tqdm_class=None, etag_timeout=30, token=TOKEN
    )
except Exception:
    restart_space()
try:
    print(EVAL_RESULTS_PATH)
    snapshot_download(
        repo_id=RESULTS_REPO, local_dir=EVAL_RESULTS_PATH, repo_type="dataset", tqdm_class=None, etag_timeout=30, token=TOKEN
    )
except Exception:
    restart_space()


raw_data, original_df = get_leaderboard_df(EVAL_RESULTS_PATH, EVAL_REQUESTS_PATH, COLS, BENCHMARK_COLS)
leaderboard_df = original_df.copy()

(
    finished_eval_queue_df,
    running_eval_queue_df,
    pending_eval_queue_df,
) = get_evaluation_queue_df(EVAL_REQUESTS_PATH, EVAL_COLS)


# Searching and filtering
def update_table(
    hidden_df: pd.DataFrame,
    columns_info: list,
    columns_IE: list,
    columns_TA: list,
    columns_QA: list,
    columns_TG: list,
    columns_RM: list,
    columns_FO: list,
    columns_DM: list,
    columns_spanish: list,
    columns_other: list,
    type_query: list,
    precision_query: list,
    size_query: list,
    show_deleted: bool,
    query: str,
):
    # Combine all column selections
    selected_columns = (
        columns_info + columns_IE + columns_TA + columns_QA + columns_TG +
        columns_RM + columns_FO + columns_DM + columns_spanish + columns_other
    )
    # Filter models based on queries
    filtered_df = filter_models(hidden_df, type_query, size_query, precision_query, show_deleted)
    filtered_df = filter_queries(query, filtered_df)
    df = select_columns(filtered_df, selected_columns)
    return df


def search_table(df: pd.DataFrame, query: str) -> pd.DataFrame:
    return df[(df[AutoEvalColumn.model.name].str.contains(query, case=False))]


def select_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    always_here_cols = [
        AutoEvalColumn.model_type_symbol.name,
        AutoEvalColumn.model.name,
    ]

    # Ensure no duplicates and add the new average columns
    unique_columns = set(always_here_cols + columns)

    # We use COLS to maintain sorting
    filtered_df = df[[c for c in COLS if c in df.columns and c in unique_columns]]

    # Debugging print to see if the new columns are included
    print(f"Columns included in DataFrame: {filtered_df.columns.tolist()}")

    return filtered_df




def filter_queries(query: str, filtered_df: pd.DataFrame) -> pd.DataFrame:
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
    else:
        filtered_df = df[df[AutoEvalColumn.still_on_hub.name] == True]

    if "All" not in type_query:
        if "?" in type_query:
            filtered_df = filtered_df.loc[~df[AutoEvalColumn.model_type_symbol.name].isin([t for t in ModelType if t != "?"])]
        else:
            type_emoji = [t[0] for t in type_query]
            filtered_df = filtered_df.loc[df[AutoEvalColumn.model_type_symbol.name].isin(type_emoji)]

    if "All" not in precision_query:
        if "?" in precision_query:
            filtered_df = filtered_df.loc[df[AutoEvalColumn.precision.name].isna()]
        else:
            filtered_df = filtered_df.loc[df[AutoEvalColumn.precision.name].isin(precision_query + ["None"])]

    if "All" not in size_query:
        if "?" in size_query:
            filtered_df = filtered_df.loc[df[AutoEvalColumn.params.name].isna()]
        else:
            numeric_interval = pd.IntervalIndex(sorted([NUMERIC_INTERVALS[s] for s in size_query]))
            params_column = pd.to_numeric(df[AutoEvalColumn.params.name], errors="coerce")
            mask = params_column.apply(lambda x: any(numeric_interval.contains(x)))
            filtered_df = filtered_df.loc[mask]

    return filtered_df



def uncheck_all():
    return [], [], [], [], [], [], [], [], [], []

# Get a list of all logo files in the directory
logos_dir = "logos"
logo_files = [f for f in os.listdir(logos_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

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
                        with gr.Accordion("Select columns to show"):
                            with gr.Tab("Model Information"):
                                shown_columns_info = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Model Information"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Model Information"],
                                    label="Model Information",
                                    interactive=True,
                                )
                            with gr.Tab("Information Extraction (IE)"):
                                shown_columns_IE = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Information Extraction (IE)"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Information Extraction (IE)"],
                                    label="Information Extraction (IE)",
                                    interactive=True,
                                )
                            with gr.Tab("Textual Analysis (TA)"):
                                shown_columns_TA = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Textual Analysis (TA)"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Textual Analysis (TA)"],
                                    label="Textual Analysis (TA)",
                                    interactive=True,
                                )
                            with gr.Tab("Question Answering (QA)"):
                                shown_columns_QA = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Question Answering (QA)"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Question Answering (QA)"],
                                    label="Question Answering (QA)",
                                    interactive=True,
                                )
                            with gr.Tab("Text Generation (TG)"):
                                shown_columns_TG = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Text Generation (TG)"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Text Generation (TG)"],
                                    label="Text Generation (TG)",
                                    interactive=True,
                                )
                            with gr.Tab("Risk Management (RM)"):
                                shown_columns_RM = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Risk Management (RM)"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Risk Management (RM)"],
                                    label="Risk Management (RM)",
                                    interactive=True,
                                )
                            with gr.Tab("Forecasting (FO)"):
                                shown_columns_FO = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Forecasting (FO)"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Forecasting (FO)"],
                                    label="Forecasting (FO)",
                                    interactive=True,
                                )
                            with gr.Tab("Decision-Making (DM)"):
                                shown_columns_DM = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Decision-Making (DM)"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Decision-Making (DM)"],
                                    label="Decision-Making (DM)",
                                    interactive=True,
                                )
                            with gr.Tab("Spanish"):
                                shown_columns_spanish = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Spanish"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Spanish"],
                                    label="Spanish",
                                    interactive=True,
                                )
                            with gr.Tab("Other"):
                                shown_columns_other = gr.CheckboxGroup(
                                    choices=[c.name for c in fields(AutoEvalColumn) if c.category == "Other"],
                                    value=[c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and c.category == "Other"],
                                    label="Other",
                                    interactive=True,
                                )
                    with gr.Row():
                        uncheck_all_button = gr.Button("Uncheck All")
                        uncheck_all_button.click(
                            uncheck_all,
                            inputs=[],
                            outputs=[
                                shown_columns_info,
                                shown_columns_IE,
                                shown_columns_TA,
                                shown_columns_QA,
                                shown_columns_TG,
                                shown_columns_RM,
                                shown_columns_FO,
                                shown_columns_DM,
                                shown_columns_spanish,
                                shown_columns_other,

                            ],
                        )
                    with gr.Row():
                        deleted_models_visibility = gr.Checkbox(
                            value=True, label="Show gated/private/deleted models", interactive=True
                        )
                with gr.Column(min_width=320):
                    #with gr.Box(elem_id="box-filter"):
                    filter_columns_type = gr.CheckboxGroup(
                        label="Model types",
                        choices=["All"] + [t.to_str() for t in ModelType],
                        value=["All"],
                        interactive=True,
                        elem_id="filter-columns-type",
                    )
                    filter_columns_precision = gr.CheckboxGroup(
                        label="Precision",
                        choices=["All"] + [i.value.name for i in Precision],
                        value=["All"],
                        interactive=True,
                        elem_id="filter-columns-precision",
                    )
                    filter_columns_size = gr.CheckboxGroup(
                        label="Model sizes (in billions of parameters)",
                        choices=["All"] + list(NUMERIC_INTERVALS.keys()) + ["?"],
                        value=["All"],
                        interactive=True,
                        elem_id="filter-columns-size",
                    )


            leaderboard_table = gr.Dataframe(
                value=leaderboard_df[
                    [c.name for c in fields(AutoEvalColumn) if c.never_hidden]
                    + [c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.never_hidden]
                ],
                headers=[c.name for c in fields(AutoEvalColumn) if c.never_hidden]
                        + [c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.never_hidden],
                datatype=TYPES,
                elem_id="leaderboard-table",
                interactive=False,
                visible=True,
            )


            # Dummy leaderboard for handling the case when the user uses backspace key
            hidden_leaderboard_table_for_search = gr.Dataframe(
                value=original_df[COLS],
                headers=COLS,
                datatype=TYPES,
                visible=False,
            )
            search_bar.submit(
                update_table,
                inputs=[
                    hidden_leaderboard_table_for_search,
                    shown_columns_info,
                    shown_columns_IE,
                    shown_columns_TA,
                    shown_columns_QA,
                    shown_columns_TG,
                    shown_columns_RM,
                    shown_columns_FO,
                    shown_columns_DM,
                    shown_columns_spanish,
                    shown_columns_other,
                    filter_columns_type,
                    filter_columns_precision,
                    filter_columns_size,
                    deleted_models_visibility,
                    search_bar,
                ],
                outputs=leaderboard_table,
            )
            for selector in [
                shown_columns_info,
                shown_columns_IE,
                shown_columns_TA,
                shown_columns_QA,
                shown_columns_TG,
                shown_columns_RM,
                shown_columns_FO,
                shown_columns_DM,
                shown_columns_spanish,
                shown_columns_other,
                filter_columns_type, filter_columns_precision, 
                filter_columns_size, deleted_models_visibility
            ]:
                selector.change(
                    update_table,
                    inputs=[
                        hidden_leaderboard_table_for_search,
                        shown_columns_info,
                        shown_columns_IE,
                        shown_columns_TA,
                        shown_columns_QA,
                        shown_columns_TG,
                        shown_columns_RM,
                        shown_columns_FO,
                        shown_columns_DM,
                        shown_columns_spanish,
                        shown_columns_other,
                        filter_columns_type,
                        filter_columns_precision,
                        filter_columns_size,
                        deleted_models_visibility,
                        search_bar,
                    ],
                    outputs=leaderboard_table,
                    queue=True,
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
                            finished_eval_table = gr.Dataframe(
                                value=finished_eval_queue_df,
                                headers=EVAL_COLS,
                                datatype=EVAL_TYPES,
                                row_count=5,
                            )
                    with gr.Accordion(
                        f"🔄 Running Evaluation Queue ({len(running_eval_queue_df)})",
                        open=False,
                    ):
                        with gr.Row():
                            running_eval_table = gr.Dataframe(
                                value=running_eval_queue_df,
                                headers=EVAL_COLS,
                                datatype=EVAL_TYPES,
                                row_count=5,
                            )

                    with gr.Accordion(
                        f"⏳ Pending Evaluation Queue ({len(pending_eval_queue_df)})",
                        open=False,
                    ):
                        with gr.Row():
                            pending_eval_table = gr.Dataframe(
                                value=pending_eval_queue_df,
                                headers=EVAL_COLS,
                                datatype=EVAL_TYPES,
                                row_count=5,
                            )
            with gr.Row():
                gr.Markdown("# ✉️✨ Submit your model here!", elem_classes="markdown-text")

            with gr.Row():
                with gr.Column():
                    model_name_textbox = gr.Textbox(label="Model name")
                    revision_name_textbox = gr.Textbox(label="Revision commit", placeholder="main")
                    model_type = gr.Dropdown(
                        choices=[t.to_str(" : ") for t in ModelType if t != ModelType.Unknown],
                        label="Model type",
                        multiselect=False,
                        value=None,
                        interactive=True,
                    )

                with gr.Column():
                    precision = gr.Dropdown(
                        choices=[i.value.name for i in Precision if i != Precision.Unknown],
                        label="Precision",
                        multiselect=False,
                        value="float16",
                        interactive=True,
                    )
                    weight_type = gr.Dropdown(
                        choices=[i.value.name for i in WeightType],
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
                    weight_type,
                    model_type,
                ],
                submission_result,
            )

    # Footer with logos
    with gr.Row(elem_id="footer"):
        for logo in logo_files:
            logo_path = os.path.join(logos_dir, logo)
            gr.Image(logo_path, show_label=False, elem_id="logo-image", width=100, height=100)

    with gr.Row():
        with gr.Accordion("📙 Citation", open=False):
            citation_button = gr.Textbox(
                value=CITATION_BUTTON_TEXT,
                label=CITATION_BUTTON_LABEL,
                lines=20,
                elem_id="citation-button",
                show_copy_button=True,
            )

scheduler = BackgroundScheduler()
scheduler.add_job(restart_space, "interval", seconds=1800)
scheduler.start()
demo.queue(default_concurrency_limit=40).launch()
