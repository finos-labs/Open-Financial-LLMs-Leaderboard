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
