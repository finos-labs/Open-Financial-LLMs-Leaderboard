from src.display.formatting import model_hyperlink
from src.display.utils import AutoEvalColumn

# Models which have been flagged by users as being problematic for a reason or another
# (Model name to forum discussion link)
FLAGGED_MODELS = {
    "Voicelab/trurl-2-13b": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/202",
    "deepnight-research/llama-2-70B-inst": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/207",
    "Aspik101/trurl-2-13b-pl-instruct_unload": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/213",
    "Fredithefish/ReasonixPajama-3B-HF": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/236",
    "TigerResearch/tigerbot-7b-sft-v1": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/237",
    "gaodrew/gaodrew-gorgonzola-13b": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/215",
    "AIDC-ai-business/Marcoroni-70B": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/287",
    "AIDC-ai-business/Marcoroni-13B": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/287",
    "AIDC-ai-business/Marcoroni-7B": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/287",
}

# Models which have been requested by orgs to not be submitted on the leaderboard
DO_NOT_SUBMIT_MODELS = [
    "Voicelab/trurl-2-13b",  # trained on MMLU
]


def flag_models(leaderboard_data: list[dict]):
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


def remove_forbidden_models(leaderboard_data: list[dict]):
    indices_to_remove = []
    for ix, model in enumerate(leaderboard_data):
        if model["model_name_for_query"] in DO_NOT_SUBMIT_MODELS:
            indices_to_remove.append(ix)

    for ix in reversed(indices_to_remove):
        leaderboard_data.pop(ix)
    return leaderboard_data


def filter_models(leaderboard_data: list[dict]):
    leaderboard_data = remove_forbidden_models(leaderboard_data)
    flag_models(leaderboard_data)
