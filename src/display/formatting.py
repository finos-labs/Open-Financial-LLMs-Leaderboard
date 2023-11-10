import os
from huggingface_hub import HfApi

API = HfApi()

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
