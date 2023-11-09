import os
from dataclasses import dataclass

from huggingface_hub import HfApi

API = HfApi()


# These classes are for user facing column names, to avoid having to change them
# all around the code when a modif is needed
@dataclass
class ColumnContent:
    name: str
    type: str
    displayed_by_default: bool
    hidden: bool = False


def fields(raw_class):
    return [v for k, v in raw_class.__dict__.items() if k[:2] != "__" and k[-2:] != "__"]


@dataclass(frozen=True)
class AutoEvalColumn:  # Auto evals column
    model_type_symbol = ColumnContent("T", "str", True)
    model = ColumnContent("Model", "markdown", True)
    average = ColumnContent("Average ⬆️", "number", True)
    arc = ColumnContent("ARC", "number", True)
    hellaswag = ColumnContent("HellaSwag", "number", True)
    mmlu = ColumnContent("MMLU", "number", True)
    truthfulqa = ColumnContent("TruthfulQA", "number", True)
    winogrande = ColumnContent("Winogrande", "number", True)
    gsm8k = ColumnContent("GSM8K", "number", True)
    drop = ColumnContent("DROP", "number", True)
    model_type = ColumnContent("Type", "str", False)
    precision = ColumnContent("Precision", "str", False)  # , True)
    license = ColumnContent("Hub License", "str", False)
    params = ColumnContent("#Params (B)", "number", False)
    likes = ColumnContent("Hub ❤️", "number", False)
    still_on_hub = ColumnContent("Available on the hub", "bool", False)
    revision = ColumnContent("Model sha", "str", False, False)
    dummy = ColumnContent(
        "model_name_for_query", "str", True
    )  # dummy col to implement search bar (hidden by custom CSS)


@dataclass(frozen=True)
class EloEvalColumn:  # Elo evals column
    model = ColumnContent("Model", "markdown", True)
    gpt4 = ColumnContent("GPT-4 (all)", "number", True)
    human_all = ColumnContent("Human (all)", "number", True)
    human_instruct = ColumnContent("Human (instruct)", "number", True)
    human_code_instruct = ColumnContent("Human (code-instruct)", "number", True)


@dataclass(frozen=True)
class EvalQueueColumn:  # Queue column
    model = ColumnContent("model", "markdown", True)
    revision = ColumnContent("revision", "str", True)
    private = ColumnContent("private", "bool", True)
    precision = ColumnContent("precision", "str", True)
    weight_type = ColumnContent("weight_type", "str", "Original")
    status = ColumnContent("status", "str", True)


LLAMAS = [
    "huggingface/llama-7b",
    "huggingface/llama-13b",
    "huggingface/llama-30b",
    "huggingface/llama-65b",
]


KOALA_LINK = "https://huggingface.co/TheBloke/koala-13B-HF"
VICUNA_LINK = "https://huggingface.co/lmsys/vicuna-13b-delta-v1.1"
OASST_LINK = "https://huggingface.co/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"
DOLLY_LINK = "https://huggingface.co/databricks/dolly-v2-12b"
MODEL_PAGE = "https://huggingface.co/models"
LLAMA_LINK = "https://ai.facebook.com/blog/large-language-model-llama-meta-ai/"
VICUNA_LINK = "https://huggingface.co/CarperAI/stable-vicuna-13b-delta"
ALPACA_LINK = "https://crfm.stanford.edu/2023/03/13/alpaca.html"


def model_hyperlink(link, model_name):
    return f'<a target="_blank" href="{link}" style="color: var(--link-text-color); text-decoration: underline;text-decoration-style: dotted;">{model_name}</a>'


def make_clickable_model(model_name):
    link = f"https://huggingface.co/{model_name}"

    if model_name in LLAMAS:
        link = LLAMA_LINK
        model_name = model_name.split("/")[1]
    elif model_name == "HuggingFaceH4/stable-vicuna-13b-2904":
        link = VICUNA_LINK
        model_name = "stable-vicuna-13b"
    elif model_name == "HuggingFaceH4/llama-7b-ift-alpaca":
        link = ALPACA_LINK
        model_name = "alpaca-13b"
    if model_name == "dolly-12b":
        link = DOLLY_LINK
    elif model_name == "vicuna-13b":
        link = VICUNA_LINK
    elif model_name == "koala-13b":
        link = KOALA_LINK
    elif model_name == "oasst-12b":
        link = OASST_LINK

    details_model_name = model_name.replace("/", "__")
    details_link = f"https://huggingface.co/datasets/open-llm-leaderboard/details_{details_model_name}"

    if not bool(os.getenv("DEBUG", "False")):
        # We only add these checks when not debugging, as they are extremely slow
        print(f"details_link: {details_link}")
        try:
            check_path = list(
                API.list_files_info(
                    repo_id=f"open-llm-leaderboard/details_{details_model_name}",
                    paths="README.md",
                    repo_type="dataset",
                )
            )
            print(f"check_path: {check_path}")
        except Exception as err:
            # No details repo for this model
            print(f"No details repo for this model: {err}")
            return model_hyperlink(link, model_name)

    return model_hyperlink(link, model_name) + "  " + model_hyperlink(details_link, "📑")


def styled_error(error):
    return f"<p style='color: red; font-size: 20px; text-align: center;'>{error}</p>"


def styled_warning(warn):
    return f"<p style='color: orange; font-size: 20px; text-align: center;'>{warn}</p>"


def styled_message(message):
    return f"<p style='color: green; font-size: 20px; text-align: center;'>{message}</p>"


def has_no_nan_values(df, columns):
    return df[columns].notna().all(axis=1)


def has_nan_values(df, columns):
    return df[columns].isna().any(axis=1)
