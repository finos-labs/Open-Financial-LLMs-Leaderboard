import os
from datetime import datetime, timezone

from huggingface_hub import HfApi
from huggingface_hub.hf_api import ModelInfo


API = HfApi()

def model_hyperlink(link, model_name):
    return f'<a target="_blank" href="{link}" style="color: var(--link-text-color); text-decoration: underline;text-decoration-style: dotted;">{model_name}</a>'


def make_clickable_model(model_name):
    link = f"https://huggingface.co/{model_name}"

    details_model_name = model_name.replace("/", "__")
    details_link = f"https://huggingface.co/datasets/open-llm-leaderboard/details_{details_model_name}"

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
