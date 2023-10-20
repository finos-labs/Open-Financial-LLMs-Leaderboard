import huggingface_hub
from huggingface_hub import ModelCard
from transformers import AutoConfig

from datetime import datetime, timedelta, timezone


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


def is_model_on_hub(model_name: str, revision: str) -> bool:
    try:
        AutoConfig.from_pretrained(model_name, revision=revision, trust_remote_code=False)
        return True, None

    except ValueError:
        return (
            False,
            "needs to be launched with `trust_remote_code=True`. For safety reason, we do not allow these models to be automatically submitted to the leaderboard.",
        )

    except Exception:
        return False, "was not found on hub!"


def user_submission_permission(submission_name, users_to_submission_dates, rate_limit_period, rate_limit_quota):
    org_or_user, _ = submission_name.split("/")
    if org_or_user not in users_to_submission_dates:
        return True, ""
    submission_dates = sorted(users_to_submission_dates[org_or_user])

    time_limit = (datetime.now(timezone.utc) - timedelta(days=rate_limit_period)).strftime("%Y-%m-%dT%H:%M:%SZ")
    submissions_after_timelimit = [d for d in submission_dates if d > time_limit]

    num_models_submitted_in_period = len(submissions_after_timelimit)
    if num_models_submitted_in_period > rate_limit_quota:
        error_msg = f"Organisation or user `{org_or_user}`"
        error_msg += f"already has {num_models_submitted_in_period} model requests submitted to the leaderboard "
        error_msg += f"in the last {rate_limit_period} days.\n"
        error_msg += (
            "Please wait a couple of days before resubmitting, so that everybody can enjoy using the leaderboard 🤗"
        )
        return False, error_msg
    return True, ""

