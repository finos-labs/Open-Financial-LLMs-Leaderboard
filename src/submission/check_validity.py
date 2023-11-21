import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import huggingface_hub
from huggingface_hub import ModelCard
from huggingface_hub.hf_api import ModelInfo
from transformers import AutoConfig
from transformers.models.auto.tokenization_auto import tokenizer_class_from_name, get_tokenizer_config

from src.envs import HAS_HIGHER_RATE_LIMIT


# ht to @Wauplin, thank you for the snippet!
# See https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/317
def check_model_card(repo_id: str) -> tuple[bool, str]:
    # Returns operation status, and error message
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
            tokenizer_config = get_tokenizer_config(model_name) 
            if tokenizer_config is not None:
                tokenizer_class_candidate = tokenizer_config.get("tokenizer_class", None)
            else:
                tokenizer_class_candidate = config.tokenizer_class 


            tokenizer_class = tokenizer_class_from_name(tokenizer_class_candidate)
            if tokenizer_class is None:
                return (
                    False,
                    f"uses {tokenizer_class_candidate}, which is not in a transformers release, therefore not supported at the moment.",
                    None
                )
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
    size_pattern = size_pattern = re.compile(r"(\d\.)?\d+(b|m)")
    try:
        model_size = round(model_info.safetensors["total"] / 1e9, 3)
    except (AttributeError, TypeError ):
        try:
            size_match = re.search(size_pattern, model_info.modelId.lower())
            model_size = size_match.group(0)
            model_size = round(float(model_size[:-1]) if model_size[-1] == "b" else float(model_size[:-1]) / 1e3, 3)
        except AttributeError:
            return 0  # Unknown model sizes are indicated as 0, see NUMERIC_INTERVALS in app.py

    size_factor = 8 if (precision == "GPTQ" or "gptq" in model_info.modelId.lower()) else 1
    model_size = size_factor * model_size
    return model_size

def get_model_arch(model_info: ModelInfo):
    return model_info.config.get("architectures", "Unknown")

def user_submission_permission(org_or_user, users_to_submission_dates, rate_limit_period, rate_limit_quota):
    if org_or_user not in users_to_submission_dates:
        return True, ""
    submission_dates = sorted(users_to_submission_dates[org_or_user])

    time_limit = (datetime.now(timezone.utc) - timedelta(days=rate_limit_period)).strftime("%Y-%m-%dT%H:%M:%SZ")
    submissions_after_timelimit = [d for d in submission_dates if d > time_limit]

    num_models_submitted_in_period = len(submissions_after_timelimit)
    if org_or_user in HAS_HIGHER_RATE_LIMIT:
        rate_limit_quota = 2 * rate_limit_quota

    if num_models_submitted_in_period > rate_limit_quota:
        error_msg = f"Organisation or user `{org_or_user}`"
        error_msg += f"already has {num_models_submitted_in_period} model requests submitted to the leaderboard "
        error_msg += f"in the last {rate_limit_period} days.\n"
        error_msg += (
            "Please wait a couple of days before resubmitting, so that everybody can enjoy using the leaderboard 🤗"
        )
        return False, error_msg
    return True, ""


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
