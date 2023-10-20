import re
from huggingface_hub.hf_api import ModelInfo


def get_model_size(model_info: ModelInfo, precision: str):
    size_pattern = size_pattern = re.compile(r"(\d\.)?\d+(b|m)")
    try:
        model_size = round(model_info.safetensors["total"] / 1e9, 3)
    except AttributeError:
        try:
            size_match = re.search(size_pattern, model_info.modelId.lower())
            model_size = size_match.group(0)
            model_size = round(float(model_size[:-1]) if model_size[-1] == "b" else float(model_size[:-1]) / 1e3, 3)
        except AttributeError:
            return 0 # Unknown model sizes are indicated as 0, see NUMERIC_INTERVALS in app.py

    size_factor = 8 if (precision == "GPTQ" or "gptq" in model_info.modelId.lower()) else 1
    model_size = size_factor * model_size
    return model_size
