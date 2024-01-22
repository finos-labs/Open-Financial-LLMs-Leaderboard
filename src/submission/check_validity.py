import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import huggingface_hub
from huggingface_hub import ModelCard
from huggingface_hub.hf_api import ModelInfo
from transformers import AutoConfig
from transformers.models.auto.tokenization_auto import AutoTokenizer

def check_model_card(repo_id: str) -> tuple[bool, str]:
    """Checks if the model card and license exist and have been filled"""
    try:
        card = ModelCard.load(repo_id)
    except huggingface_hub.utils.EntryNotFoundError:
        return False, "Please add a model card to your model to explain how you trained/fine-tuned it."

    # Enforce license metadata
    if card.data.license is None:
        if not ("license_name" in card.data and "license_link" in card.data):
            return False, (
                "License not found. Please add a license to your model card using the `license` metadata or a"
                " `license_name`/`license_link` pair."
            )

    # Enforce card content
    if len(card.text) < 200:
        return False, "Please add a description to your model card, it is too short."

    return True, ""

def is_model_on_hub(model_name: str, revision: str, token: str = None, trust_remote_code=False, test_tokenizer=False) -> tuple[bool, str]:
    try:
        config = AutoConfig.from_pretrained(model_name, revision=revision, trust_remote_code=trust_remote_code, token=token)
        if test_tokenizer:
            try:
                tk = AutoTokenizer.from_pretrained(model_name, revision=revision, trust_remote_code=trust_remote_code, token=token)
            except ValueError as e:
                return (
                    False,
                    f"uses a tokenizer which is not in a transformers release: {e}",
                    None
                )
            except Exception as e:
                return (False, "'s tokenizer cannot be loaded. Is your tokenizer class in a stable transformers release, and correctly configured?", None)
        return True, None, config

    except ValueError:
        return (
            False,
            "needs to be launched with `trust_remote_code=True`. For safety reason, we do not allow these models to be automatically submitted to the leaderboard.",
            None
        )

    except Exception as e:
        return False, "was not found on hub!", None


def get_model_size(model_info: ModelInfo, precision: str):
    """Gets the model size from the configuration, or the model name if the configuration does not contain the information."""
    try:
        model_size = round(model_info.safetensors["total"] / 1e9, 3)
    except (AttributeError, TypeError):
        return 0  # Unknown model sizes are indicated as 0, see NUMERIC_INTERVALS in app.py

    size_factor = 8 if (precision == "GPTQ" or "gptq" in model_info.modelId.lower()) else 1
    model_size = size_factor * model_size
    return model_size

def get_model_arch(model_info: ModelInfo):
    """Gets the model architecture from the configuration"""
    return model_info.config.get("architectures", "Unknown")

def already_submitted_models(requested_models_dir: str) -> set[str]:
    depth = 1
    file_names = []
    users_to_submission_dates = defaultdict(list)

    for root, _, files in os.walk(requested_models_dir):
        current_depth = root.count(os.sep) - requested_models_dir.count(os.sep)
        if current_depth == depth:
            for file in files:
                if not file.endswith(".json"):
                    continue
                with open(os.path.join(root, file), "r") as f:
                    info = json.load(f)
                    file_names.append(f"{info['model']}_{info['revision']}_{info['precision']}")

                    # Select organisation
                    if info["model"].count("/") == 0 or "submitted_time" not in info:
                        continue
                    organisation, _ = info["model"].split("/")
                    users_to_submission_dates[organisation].append(info["submitted_time"])

    return set(file_names), users_to_submission_dates
