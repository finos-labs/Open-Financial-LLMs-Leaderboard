from dataclasses import dataclass

# These classes are for user facing column names, to avoid having to change them 
# all around the code when a modif is needed 
@dataclass
class ColumnContent:
    name: str
    type: str 
    displayed_by_default: bool 
    hidden: bool = False

def fields(raw_class):
    return [v for k, v in raw_class.__dict__.items() if k[:2] != "__" and k[-2:] != "__"]

@dataclass(frozen=True)
class AutoEvalColumn: # Auto evals column
    model = ColumnContent("Model", "markdown", True)
    average = ColumnContent("Average ⬆️", "number", True)
    arc = ColumnContent("ARC ⬆️", "number", True)
    hellaswag = ColumnContent("HellaSwag ⬆️", "number", True)
    mmlu = ColumnContent("MMLU ⬆️", "number", True)
    truthfulqa = ColumnContent("TruthfulQA (MC) ⬆️", "number", True)
    model_type = ColumnContent("Type", "bool", False)
    is_8bit = ColumnContent("8bit", "bool", False, True)
    license = ColumnContent("Hub License", "str", False)
    params = ColumnContent("#Params (B)", "number", False)
    likes = ColumnContent("Hub ❤️", "number", False)
    revision = ColumnContent("Model sha", "str", False, False)
    dummy = ColumnContent("model_name_for_query", "str", True) # dummy col to implement search bar (hidden by custom CSS)

@dataclass(frozen=True)
class EloEvalColumn: # Elo evals column
    model = ColumnContent("Model", "markdown", True)
    gpt4 = ColumnContent("GPT-4 (all)", "number", True)
    human_all = ColumnContent("Human (all)", "number", True)
    human_instruct = ColumnContent("Human (instruct)", "number", True)
    human_code_instruct = ColumnContent("Human (code-instruct)", "number", True)


@dataclass(frozen=True)
class EvalQueueColumn: # Queue column
    model = ColumnContent("model", "markdown", True)
    revision = ColumnContent("revision", "str", True)
    private = ColumnContent("private", "bool", True)
    is_8bit = ColumnContent("8bit_eval", "bool", True)
    has_delta_weight = ColumnContent("is_delta_weight", "bool", True)
    status = ColumnContent("status", "str", True)

LLAMAS = ["huggingface/llama-7b", "huggingface/llama-13b", "huggingface/llama-30b", "huggingface/llama-65b"]


KOALA_LINK = "https://huggingface.co/TheBloke/koala-13B-HF"
VICUNA_LINK = "https://huggingface.co/lmsys/vicuna-13b-delta-v1.1"
OASST_LINK = "https://huggingface.co/OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5"
DOLLY_LINK = "https://huggingface.co/databricks/dolly-v2-12b"
MODEL_PAGE = "https://huggingface.co/models"
LLAMA_LINK = "https://ai.facebook.com/blog/large-language-model-llama-meta-ai/"
VICUNA_LINK = "https://huggingface.co/CarperAI/stable-vicuna-13b-delta"
ALPACA_LINK = "https://crfm.stanford.edu/2023/03/13/alpaca.html"


def model_hyperlink(link, model_name):
    return f'<a target="_blank" href="{link}" style="color: var(--link-text-color); text-decoration: underline;text-decoration-style: dotted;">{model_name}</a>'


def make_clickable_model(model_name):
    link = f"https://huggingface.co/{model_name}"

    if model_name in LLAMAS:
        link = LLAMA_LINK
        model_name = model_name.split("/")[1]
    elif model_name == "HuggingFaceH4/stable-vicuna-13b-2904":
        link = VICUNA_LINK
        model_name = "stable-vicuna-13b"
    elif model_name == "HuggingFaceH4/llama-7b-ift-alpaca":
        link = ALPACA_LINK
        model_name = "alpaca-13b"
    if model_name == "dolly-12b":
        link = DOLLY_LINK
    elif model_name == "vicuna-13b":
        link = VICUNA_LINK
    elif model_name == "koala-13b":
        link = KOALA_LINK
    elif model_name == "oasst-12b":
        link = OASST_LINK
    #else:
    #    link = MODEL_PAGE
  
    return model_hyperlink(link, model_name)

def styled_error(error):
    return f"<p style='color: red; font-size: 20px; text-align: center;'>{error}</p>"

def styled_warning(warn):
    return f"<p style='color: orange; font-size: 20px; text-align: center;'>{warn}</p>"

def styled_message(message):
    return f"<p style='color: green; font-size: 20px; text-align: center;'>{message}</p>"