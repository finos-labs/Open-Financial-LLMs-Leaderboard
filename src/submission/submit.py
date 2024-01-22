import json
import os
from datetime import datetime, timezone

from src.display.formatting import styled_error, styled_message, styled_warning
from src.envs import API, EVAL_REQUESTS_PATH, TOKEN, QUEUE_REPO
from src.submission.check_validity import (
    already_submitted_models,
    check_model_card,
    get_model_size,
    is_model_on_hub,
)

REQUESTED_MODELS = None
USERS_TO_SUBMISSION_DATES = None

def add_new_eval(
    model: str,
    base_model: str,
    revision: str,
    precision: str,
    weight_type: str,
    model_type: str,
):
    global REQUESTED_MODELS
    global USERS_TO_SUBMISSION_DATES
    if not REQUESTED_MODELS:
        REQUESTED_MODELS, USERS_TO_SUBMISSION_DATES = already_submitted_models(EVAL_REQUESTS_PATH)

    user_name = ""
    model_path = model
    if "/" in model:
        user_name = model.split("/")[0]
        model_path = model.split("/")[1]

    precision = precision.split(" ")[0]
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if model_type is None or model_type == "":
        return styled_error("Please select a model type.")

    # Does the model actually exist?
    if revision == "":
        revision = "main"

    # Is the model on the hub?
    if weight_type in ["Delta", "Adapter"]:
        base_model_on_hub, error, _ = is_model_on_hub(model_name=base_model, revision=revision, token=TOKEN, test_tokenizer=True)
        if not base_model_on_hub:
            return styled_error(f'Base model "{base_model}" {error}')

    if not weight_type == "Adapter":
        model_on_hub, error, _ = is_model_on_hub(model_name=model, revision=revision, token=TOKEN, test_tokenizer=True)
        if not model_on_hub:
            return styled_error(f'Model "{model}" {error}')

    # Is the model info correctly filled?
    try:
        model_info = API.model_info(repo_id=model, revision=revision)
    except Exception:
        return styled_error("Could not get your model information. Please fill it up properly.")

    model_size = get_model_size(model_info=model_info, precision=precision)

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
        "precision": precision,
        "weight_type": weight_type,
        "status": "PENDING",
        "submitted_time": current_time,
        "model_type": model_type,
        "likes": model_info.likes,
        "params": model_size,
        "license": license,
        "private": False,
    }

    # Check for duplicate submission
    if f"{model}_{revision}_{precision}" in REQUESTED_MODELS:
        return styled_warning("This model has been already submitted.")

    print("Creating eval file")
    OUT_DIR = f"{EVAL_REQUESTS_PATH}/{user_name}"
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/{model_path}_eval_request_False_{precision}_{weight_type}.json"

    with open(out_path, "w") as f:
        f.write(json.dumps(eval_entry))

    print("Uploading eval file")
    API.upload_file(
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
