import re
import os
from typing import List

from src.utils_display import AutoEvalColumn
from src.auto_leaderboard.model_metadata_type import get_model_type

from huggingface_hub import HfApi
import huggingface_hub
api = HfApi(token=os.environ.get("H4_TOKEN", None))


def get_model_infos_from_hub(leaderboard_data: List[dict]):
    for model_data in leaderboard_data:
        model_name = model_data["model_name_for_query"]
        try:
            model_info = api.model_info(model_name)
        except huggingface_hub.utils._errors.RepositoryNotFoundError:
            print("Repo not found!", model_name)
            model_data[AutoEvalColumn.license.name] = None
            model_data[AutoEvalColumn.likes.name] = None
            model_data[AutoEvalColumn.params.name] = get_model_size(model_name, None)
            continue

        model_data[AutoEvalColumn.license.name] = get_model_license(model_info)
        model_data[AutoEvalColumn.likes.name] = get_model_likes(model_info)
        model_data[AutoEvalColumn.params.name] = get_model_size(model_name, model_info)


def get_model_license(model_info):
    try:
        return model_info.cardData["license"]
    except Exception:
        return None

def get_model_likes(model_info):
    return model_info.likes

size_pattern = re.compile(r"\d+(b|m)")

def get_model_size(model_name, model_info):
    # In billions
    try:
        return round(model_info.safetensors["total"] / 1e9, 3) 
    except AttributeError:
        try:
            size_match = re.search(size_pattern, model_name.lower())
            size = size_match.group(0)
            return round(int(size[:-1]) if size[-1] == "b" else int(size[:-1]) / 1e3, 3)
        except AttributeError:
            return None


def apply_metadata(leaderboard_data: List[dict]):
    get_model_type(leaderboard_data)
    get_model_infos_from_hub(leaderboard_data)
