from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

from ..utils_display import AutoEvalColumn

@dataclass
class ModelInfo:
    name: str
    symbol: str # emoji


class ModelType(Enum):
    PT = ModelInfo(name="pretrained", symbol="🟢")
    SFT = ModelInfo(name="finetuned", symbol="🔶")
    RL = ModelInfo(name="with RL", symbol="🟦")


TYPE_METADATA: Dict[str, ModelType] = {
    "aisquared/dlite-v1-355m": ModelType.SFT,
    "aisquared/dlite-v2-774m": ModelType.SFT,
    "aisquared/dlite-v2-1_5b": ModelType.SFT,
    "TheBloke/wizardLM-7B-HF": ModelType.SFT,
    "TheBloke/dromedary-65b-lora-HF": ModelType.SFT,
    "TheBloke/vicuna-13B-1.1-HF": ModelType.SFT,
    "TheBloke/Wizard-Vicuna-13B-Uncensored-HF": ModelType.SFT,
    "wordcab/llama-natural-instructions-13b": ModelType.SFT,
    "JosephusCheung/Guanaco": ModelType.SFT,
    "AlekseyKorshuk/vicuna-7b": ModelType.SFT,
    "AlekseyKorshuk/chatml-pyg-v1": ModelType.SFT,
    "concedo/OPT-19M-ChatSalad": ModelType.SFT,
    "digitous/Javalion-R": ModelType.SFT,
    "digitous/Alpacino30b": ModelType.SFT,
    "digitous/Javelin-GPTJ": ModelType.SFT,
    "anton-l/gpt-j-tiny-random": ModelType.SFT,
    "IDEA-CCNL/Ziya-LLaMA-13B-Pretrain-v1": ModelType.SFT,
    "gpt2-medium": ModelType.PT,
    "PygmalionAI/pygmalion-6b": ModelType.SFT,
    "medalpaca/medalpaca-7b": ModelType.SFT,
    "medalpaca/medalpaca-13b": ModelType.SFT,
    "chavinlo/alpaca-13b": ModelType.SFT,
    "chavinlo/alpaca-native": ModelType.SFT,
    "chavinlo/gpt4-x-alpaca": ModelType.SFT,
    "hakurei/lotus-12B": ModelType.SFT,
    "amazon/LightGPT": ModelType.SFT,
    "shibing624/chinese-llama-plus-13b-hf": ModelType.SFT,
    "mosaicml/mpt-7b": ModelType.PT,
    "PSanni/Deer-3b": ModelType.SFT,
    "bigscience/bloom-1b1": ModelType.PT,
    "MetaIX/GPT4-X-Alpasta-30b": ModelType.SFT,
    "EleutherAI/gpt-neox-20b": ModelType.PT,
    "EleutherAI/gpt-j-6b": ModelType.PT,
    "roneneldan/TinyStories-28M": ModelType.SFT,
    "lmsys/vicuna-13b-delta-v1.1": ModelType.SFT,
    "lmsys/vicuna-7b-delta-v1.1": ModelType.SFT,
    "abhiramtirumala/DialoGPT-sarcastic-medium": ModelType.SFT,
    "pillowtalks-ai/delta13b": ModelType.SFT,
    "bigcode/starcoderplus": ModelType.SFT,
    "microsoft/DialoGPT-large": ModelType.SFT,
    "microsoft/CodeGPT-small-py": ModelType.SFT,
    "Pirr/pythia-13b-deduped-green_devil": ModelType.SFT,
    "Aeala/GPT4-x-AlpacaDente2-30b": ModelType.SFT,
    "Aeala/VicUnlocked-alpaca-30b": ModelType.SFT,
    "dvruette/llama-13b-pretrained-sft-epoch-2": ModelType.SFT,
    "dvruette/oasst-gpt-neox-20b-1000-steps": ModelType.SFT,
    "openlm-research/open_llama_3b_350bt_preview": ModelType.PT,
    "openlm-research/open_llama_7b_700bt_preview": ModelType.PT,
    "openlm-research/open_llama_7b": ModelType.PT,
    "openlm-research/open_llama_3b": ModelType.PT,
    "openlm-research/open_llama_7b_400bt_preview": ModelType.PT,
    "PocketDoc/Dans-PileOfSets-Mk1-llama-13b-merged": ModelType.SFT,
    "GeorgiaTechResearchInstitute/galactica-6.7b-evol-instruct-70k": ModelType.SFT,
    "databricks/dolly-v2-7b": ModelType.SFT,
    "databricks/dolly-v2-3b": ModelType.SFT,
    "databricks/dolly-v2-12b": ModelType.SFT,
    "pinkmanlove/llama-65b-hf": ModelType.SFT,
    "Rachneet/gpt2-xl-alpaca": ModelType.SFT,
    "Locutusque/gpt2-conversational-or-qa": ModelType.SFT,
    "NbAiLab/nb-gpt-j-6B-alpaca": ModelType.SFT,
    "Fredithefish/ScarletPajama-3B-HF": ModelType.SFT,
    "eachadea/vicuna-7b-1.1": ModelType.SFT,
    "eachadea/vicuna-13b": ModelType.SFT,
    "openaccess-ai-collective/wizard-mega-13b": ModelType.SFT,
    "openaccess-ai-collective/manticore-13b": ModelType.SFT,
    "openaccess-ai-collective/manticore-30b-chat-pyg-alpha": ModelType.SFT,
    "openaccess-ai-collective/minotaur-13b": ModelType.SFT,
    "lamini/instruct-tuned-3b": ModelType.SFT,
    "pythainlp/wangchanglm-7.5B-sft-enth": ModelType.SFT,
    "pythainlp/wangchanglm-7.5B-sft-en-sharded": ModelType.SFT,
    "stabilityai/stablelm-tuned-alpha-7b": ModelType.SFT,
    "CalderaAI/30B-Lazarus": ModelType.SFT,
    "KoboldAI/OPT-13B-Nerybus-Mix": ModelType.SFT,
    "distilgpt2": ModelType.PT,
    "wahaha1987/llama_7b_sharegpt94k_fastchat": ModelType.SFT,
    "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5": ModelType.SFT,
    "junelee/wizard-vicuna-13b": ModelType.SFT,
    "BreadAi/StoryPy": ModelType.SFT,
    "togethercomputer/RedPajama-INCITE-Base-3B-v1": ModelType.PT,
    "togethercomputer/RedPajama-INCITE-Base-7B-v0.1": ModelType.PT,
    "Writer/camel-5b-hf": ModelType.SFT,
    "Writer/palmyra-base": ModelType.PT,
    "MBZUAI/lamini-neo-125m": ModelType.SFT,
    "TehVenom/DiffMerge_Pygmalion_Main-onto-V8P4": ModelType.SFT,
    "vicgalle/gpt2-alpaca-gpt4": ModelType.SFT,
    "facebook/opt-350m": ModelType.PT,
    "facebook/opt-125m": ModelType.PT,
    "facebook/opt-13b": ModelType.PT,
    "facebook/opt-1.3b": ModelType.PT,
    "facebook/opt-66b": ModelType.PT,
    "facebook/galactica-120b": ModelType.PT,
    "Abe13/jgpt2-v1": ModelType.SFT,
    "gpt2-xl": ModelType.PT,
    "HuggingFaceH4/stable-vicuna-13b-2904": ModelType.RL,
    "HuggingFaceH4/llama-7b-ift-alpaca": ModelType.SFT,
    "HuggingFaceH4/starchat-alpha": ModelType.SFT,
    "HuggingFaceH4/starchat-beta": ModelType.SFT,
    "ausboss/Llama30B-SuperHOT": ModelType.SFT,
    "ausboss/llama-13b-supercot": ModelType.SFT,
    "ausboss/llama-30b-supercot": ModelType.SFT,
    "Neko-Institute-of-Science/metharme-7b": ModelType.SFT,
    "SebastianSchramm/Cerebras-GPT-111M-instruction": ModelType.SFT,
    "victor123/WizardLM-13B-1.0": ModelType.SFT,
    "AlpinDale/pygmalion-instruct": ModelType.SFT,
    "tiiuae/falcon-7b-instruct": ModelType.SFT,
    "tiiuae/falcon-40b-instruct": ModelType.SFT,
    "tiiuae/falcon-40b": ModelType.PT,
    "tiiuae/falcon-7b": ModelType.PT,
    "cyl/awsome-llama": ModelType.SFT,
    "xzuyn/Alpacino-SuperCOT-13B": ModelType.SFT,
    "xzuyn/MedicWizard-7B": ModelType.SFT,
    "beomi/KoAlpaca-Polyglot-5.8B": ModelType.SFT,
    "chainyo/alpaca-lora-7b": ModelType.SFT,
    "Salesforce/codegen-16B-nl": ModelType.PT,
    "Salesforce/codegen-16B-multi": ModelType.SFT,
    "ai-forever/rugpt3large_based_on_gpt2": ModelType.SFT,
    "gpt2-large": ModelType.PT,
    "huggingface/llama-13b": ModelType.PT,
    "huggingface/llama-7b": ModelType.PT,
    "huggingface/llama-65b": ModelType.PT,
    "huggingface/llama-30b": ModelType.PT,
    "jondurbin/airoboros-7b": ModelType.SFT,
    "jondurbin/airoboros-13b": ModelType.SFT,
    "cerebras/Cerebras-GPT-1.3B": ModelType.PT,
    "cerebras/Cerebras-GPT-111M": ModelType.PT,
    "NousResearch/Nous-Hermes-13b": ModelType.SFT,
    "project-baize/baize-v2-7b": ModelType.SFT,
    "project-baize/baize-v2-13b": ModelType.SFT,
    "LLMs/AlpacaGPT4-7B-elina": ModelType.SFT,
    "LLMs/Vicuna-EvolInstruct-13B": ModelType.SFT,
    "huggingtweets/jerma985": ModelType.SFT,
    "huggyllama/llama-65b": ModelType.PT,
    "WizardLM/WizardLM-13B-1.0": ModelType.SFT,
    "gpt2": ModelType.PT,
    "alessandropalla/instruct_gpt2": ModelType.SFT,
    "MayaPH/FinOPT-Lincoln": ModelType.SFT,
    "MayaPH/FinOPT-Franklin": ModelType.SFT,
    "timdettmers/guanaco-33b-merged": ModelType.SFT,
    "timdettmers/guanaco-65b-merged": ModelType.SFT,
    "elinas/llama-30b-hf-transformers-4.29": ModelType.SFT,
    "elinas/chronos-33b": ModelType.SFT,
    "nmitchko/medguanaco-65b-GPTQ": ModelType.SFT,
    "xhyi/PT_GPTNEO350_ATG": ModelType.SFT,
    "h2oai/h2ogpt-oasst1-512-20b": ModelType.SFT,
    "h2oai/h2ogpt-gm-oasst1-en-1024-12b": ModelType.SFT,
    "nomic-ai/gpt4all-13b-snoozy": ModelType.SFT,
    "nomic-ai/gpt4all-j": ModelType.SFT,
}


def get_model_type(leaderboard_data: List[dict]):
    for model_data in leaderboard_data:
        # Todo @clefourrier once requests are connected with results 
        is_delta = False # (model_data["weight_type"] != "Original")
        # Stored information
        if model_data["model_name_for_query"] in TYPE_METADATA:
            model_data[AutoEvalColumn.model_type.name] = TYPE_METADATA[model_data["model_name_for_query"]].value.name
            model_data[AutoEvalColumn.model_type_symbol.name] = TYPE_METADATA[model_data["model_name_for_query"]].value.symbol + ("🔺" if is_delta else "")
        # Inferred from the name or the selected type 
        elif model_data[AutoEvalColumn.model_type.name] == "pretrained" or  any([i in model_data["model_name_for_query"] for i in ["pretrained"]]):
            model_data[AutoEvalColumn.model_type.name] = ModelType.PT.value.name
            model_data[AutoEvalColumn.model_type_symbol.name] = ModelType.PT.value.symbol + ("🔺" if is_delta else "")
        elif model_data[AutoEvalColumn.model_type.name] == "finetuned" or any([i in model_data["model_name_for_query"] for i in ["finetuned", "-ft-"]]):
            model_data[AutoEvalColumn.model_type.name] = ModelType.SFT.value.name
            model_data[AutoEvalColumn.model_type_symbol.name] = ModelType.SFT.value.symbol + ("🔺" if is_delta else "")
        elif model_data[AutoEvalColumn.model_type.name] == "with RL" or any([i in model_data["model_name_for_query"] for i in ["-rl-", "-rlhf-"]]):
            model_data[AutoEvalColumn.model_type.name] = ModelType.RL.value.name
            model_data[AutoEvalColumn.model_type_symbol.name] = ModelType.RL.value.symbol + ("🔺" if is_delta else "")
        else:
            model_data[AutoEvalColumn.model_type.name] = "N/A"
            model_data[AutoEvalColumn.model_type_symbol.name] = ("🔺" if is_delta else "")
 
 