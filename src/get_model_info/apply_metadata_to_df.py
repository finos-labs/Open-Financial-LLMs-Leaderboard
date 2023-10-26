import glob
import json
import os
from typing import List

from huggingface_hub import HfApi
from tqdm import tqdm

from src.get_model_info.hardocded_metadata.flags import DO_NOT_SUBMIT_MODELS, FLAGGED_MODELS
from src.get_model_info.hardocded_metadata.types import MODEL_TYPE_METADATA, ModelType, model_type_from_str
from src.get_model_info.utils import AutoEvalColumn, model_hyperlink

api = HfApi(token=os.environ.get("H4_TOKEN", None))


def get_model_metadata(leaderboard_data: List[dict]):
    for model_data in tqdm(leaderboard_data):
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
                        req_content["status"] in ["FINISHED", "PENDING_NEW_EVAL"]
                        and req_content["precision"] == model_data["Precision"].split(".")[-1]
                    ):
                        request_file = tmp_request_file

        try:
            with open(request_file, "r") as f:
                request = json.load(f)
            model_type = model_type_from_str(request.get("model_type", ""))
            model_data[AutoEvalColumn.model_type.name] = model_type.value.name
            model_data[AutoEvalColumn.model_type_symbol.name] = model_type.value.symbol  # + ("🔺" if is_delta else "")
            model_data[AutoEvalColumn.license.name] = request.get("license", "?")
            model_data[AutoEvalColumn.likes.name] = request.get("likes", 0)
            model_data[AutoEvalColumn.params.name] = request.get("params", 0)
        except Exception:
            print(f"Could not find request file for {model_data['model_name_for_query']}")

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

            # if we cannot find a request file, set license and likes to unknown
            model_data[AutoEvalColumn.license.name] =  "?"
            model_data[AutoEvalColumn.likes.name] = 0
            model_data[AutoEvalColumn.params.name] =  0


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
    get_model_metadata(leaderboard_data)
    flag_models(leaderboard_data)
