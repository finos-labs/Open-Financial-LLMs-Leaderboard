import glob
import json
import os
import re
import pickle
from typing import List

import huggingface_hub
from huggingface_hub import HfApi
from tqdm import tqdm
from transformers import AutoModel, AutoConfig
from accelerate import init_empty_weights

from src.display_models.model_metadata_flags import DO_NOT_SUBMIT_MODELS, FLAGGED_MODELS
from src.display_models.model_metadata_type import MODEL_TYPE_METADATA, ModelType, model_type_from_str
from src.display_models.utils import AutoEvalColumn, model_hyperlink

api = HfApi(token=os.environ.get("H4_TOKEN", None))


def get_model_infos_from_hub(leaderboard_data: List[dict]):
    # load cache from disk
    try:
        with open("model_info_cache.pkl", "rb") as f:
            model_info_cache = pickle.load(f)
    except (EOFError, FileNotFoundError):
        model_info_cache = {}
    try:
        with open("model_size_cache.pkl", "rb") as f:
            model_size_cache = pickle.load(f)
    except (EOFError, FileNotFoundError):
        model_size_cache = {}

    for model_data in tqdm(leaderboard_data):
        model_name = model_data["model_name_for_query"]

        if model_name in model_info_cache:
            model_info = model_info_cache[model_name]
        else:
            try:
                model_info = api.model_info(model_name)
                model_info_cache[model_name] = model_info
            except huggingface_hub.utils._errors.RepositoryNotFoundError:
                print("Repo not found!", model_name)
                model_data[AutoEvalColumn.license.name] = None
                model_data[AutoEvalColumn.likes.name] = None
                if model_name not in model_size_cache:
                    model_size_cache[model_name] = get_model_size(model_name, None)
                model_data[AutoEvalColumn.params.name] = model_size_cache[model_name]

        model_data[AutoEvalColumn.license.name] = get_model_license(model_info)
        model_data[AutoEvalColumn.likes.name] = get_model_likes(model_info)
        if model_name not in model_size_cache:
            model_size_cache[model_name] = get_model_size(model_name, model_info)
        model_data[AutoEvalColumn.params.name] = model_size_cache[model_name]

    # save cache to disk in pickle format
    with open("model_info_cache.pkl", "wb") as f:
        pickle.dump(model_info_cache, f)
    with open("model_size_cache.pkl", "wb") as f:
        pickle.dump(model_size_cache, f)


def get_model_license(model_info):
    try:
        return model_info.cardData["license"]
    except Exception:
        return "?"


def get_model_likes(model_info):
    return model_info.likes


size_pattern = re.compile(r"(\d\.)?\d+(b|m)")


def get_model_size(model_name, model_info):
    # In billions
    try:
        return round(model_info.safetensors["total"] / 1e9, 3)
    except AttributeError:
        try:
            config = AutoConfig.from_pretrained(model_name, trust_remote_code=False)
            with init_empty_weights():
                model = AutoModel.from_config(config, trust_remote_code=False)
            return round(sum(p.numel() for p in model.parameters() if p.requires_grad) / 1e9, 3)
        except (EnvironmentError, ValueError, KeyError):  # model config not found, likely private
            try:
                size_match = re.search(size_pattern, model_name.lower())
                size = size_match.group(0)
                return round(float(size[:-1]) if size[-1] == "b" else float(size[:-1]) / 1e3, 3)
            except AttributeError:
                return 0


def get_model_type(leaderboard_data: List[dict]):
    for model_data in leaderboard_data:
        request_files = os.path.join(
            "eval-queue",
            model_data["model_name_for_query"] + "_eval_request_*" + ".json",
        )
        request_files = glob.glob(request_files)

        # Select correct request file (precision)
        request_file = ""
        if len(request_files) == 1:
            request_file = request_files[0]
        elif len(request_files) > 1:
            request_files = sorted(request_files, reverse=True)
            for tmp_request_file in request_files:
                with open(tmp_request_file, "r") as f:
                    req_content = json.load(f)
                    if (
                        req_content["status"] == "FINISHED"
                        and req_content["precision"] == model_data["Precision"].split(".")[-1]
                    ):
                        request_file = tmp_request_file

        try:
            with open(request_file, "r") as f:
                request = json.load(f)
            model_type = model_type_from_str(request["model_type"])
            model_data[AutoEvalColumn.model_type.name] = model_type.value.name
            model_data[AutoEvalColumn.model_type_symbol.name] = model_type.value.symbol  # + ("🔺" if is_delta else "")
        except Exception:
            if model_data["model_name_for_query"] in MODEL_TYPE_METADATA:
                model_data[AutoEvalColumn.model_type.name] = MODEL_TYPE_METADATA[
                    model_data["model_name_for_query"]
                ].value.name
                model_data[AutoEvalColumn.model_type_symbol.name] = MODEL_TYPE_METADATA[
                    model_data["model_name_for_query"]
                ].value.symbol  # + ("🔺" if is_delta else "")
            else:
                model_data[AutoEvalColumn.model_type.name] = ModelType.Unknown.value.name
                model_data[AutoEvalColumn.model_type_symbol.name] = ModelType.Unknown.value.symbol


def flag_models(leaderboard_data: List[dict]):
    for model_data in leaderboard_data:
        if model_data["model_name_for_query"] in FLAGGED_MODELS:
            issue_num = FLAGGED_MODELS[model_data["model_name_for_query"]].split("/")[-1]
            issue_link = model_hyperlink(
                FLAGGED_MODELS[model_data["model_name_for_query"]],
                f"See discussion #{issue_num}",
            )
            model_data[
                AutoEvalColumn.model.name
            ] = f"{model_data[AutoEvalColumn.model.name]} has been flagged! {issue_link}"


def remove_forbidden_models(leaderboard_data: List[dict]):
    indices_to_remove = []
    for ix, model in enumerate(leaderboard_data):
        if model["model_name_for_query"] in DO_NOT_SUBMIT_MODELS:
            indices_to_remove.append(ix)

    for ix in reversed(indices_to_remove):
        leaderboard_data.pop(ix)
    return leaderboard_data


def apply_metadata(leaderboard_data: List[dict]):
    leaderboard_data = remove_forbidden_models(leaderboard_data)
    get_model_type(leaderboard_data)
    get_model_infos_from_hub(leaderboard_data)
    flag_models(leaderboard_data)
