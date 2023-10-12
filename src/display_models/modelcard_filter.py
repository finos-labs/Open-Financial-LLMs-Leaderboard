import huggingface_hub
from huggingface_hub import ModelCard


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
