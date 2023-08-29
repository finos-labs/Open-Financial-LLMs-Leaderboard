# Models which have been flagged by users as being problematic for a reason or another
# (Model name to forum discussion link)
FLAGGED_MODELS = {
    "Voicelab/trurl-2-13b": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/202",
    "deepnight-research/llama-2-70B-inst": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/207",
    "Aspik101/trurl-2-13b-pl-instruct_unload": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/213",
    "Fredithefish/ReasonixPajama-3B-HF": "https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard/discussions/236",
}

# Models which have been requested by orgs to not be submitted on the leaderboard
DO_NOT_SUBMIT_MODELS = [
    "Voicelab/trurl-2-13b",  # trained on MMLU
]
