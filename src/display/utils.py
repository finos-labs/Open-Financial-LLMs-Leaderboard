from dataclasses import dataclass, make_dataclass
from enum import Enum

import pandas as pd

def fields(raw_class):
    return [v for k, v in raw_class.__dict__.items() if k[:2] != "__" and k[-2:] != "__"]


@dataclass
class Task:
    benchmark: str
    metric: str
    col_name: str

class Tasks(Enum):
    arc = Task("arc:challenge", "acc_norm", "ARC")
    hellaswag = Task("hellaswag", "acc_norm", "HellaSwag")
    mmlu = Task("hendrycksTest", "acc", "MMLU")
    truthfulqa = Task("truthfulqa:mc", "mc2", "TruthfulQA")
    winogrande = Task("winogrande", "acc", "Winogrande")
    gsm8k = Task("gsm8k", "acc", "GSM8K")
    drop = Task("drop", "f1", "DROP")

# These classes are for user facing column names,
# to avoid having to change them all around the code
# when a modif is needed
@dataclass
class ColumnContent:
    name: str
    type: str
    displayed_by_default: bool
    hidden: bool = False
    never_hidden: bool = False
    dummy: bool = False

auto_eval_column_dict = []
# Init
auto_eval_column_dict.append(["model_type_symbol", ColumnContent, ColumnContent("T", "str", True, never_hidden=True)])
auto_eval_column_dict.append(["model", ColumnContent, ColumnContent("Model", "markdown", True, never_hidden=True)])
#Scores
auto_eval_column_dict.append(["average", ColumnContent, ColumnContent("Average ⬆️", "number", True)])
for task in Tasks:
    auto_eval_column_dict.append([task.name, ColumnContent, ColumnContent(task.value.col_name, "number", True)])
# Model information
auto_eval_column_dict.append(["model_type", ColumnContent, ColumnContent("Type", "str", False)])
auto_eval_column_dict.append(["architecture", ColumnContent, ColumnContent("Architecture", "str", False)])
auto_eval_column_dict.append(["weight_type", ColumnContent, ColumnContent("Weight type", "str", False, True)])
auto_eval_column_dict.append(["precision", ColumnContent, ColumnContent("Precision", "str", False)])
auto_eval_column_dict.append(["license", ColumnContent, ColumnContent("Hub License", "str", False)])
auto_eval_column_dict.append(["params", ColumnContent, ColumnContent("#Params (B)", "number", False)])
auto_eval_column_dict.append(["likes", ColumnContent, ColumnContent("Hub ❤️", "number", False)])
auto_eval_column_dict.append(["still_on_hub", ColumnContent, ColumnContent("Available on the hub", "bool", False)])
auto_eval_column_dict.append(["revision", ColumnContent, ColumnContent("Model sha", "str", False, False)])
# Dummy column for the search bar (hidden by the custom CSS)
auto_eval_column_dict.append(["dummy", ColumnContent, ColumnContent("model_name_for_query", "str", False, dummy=True)])

# We use make dataclass to dynamically fill the scores from Tasks
AutoEvalColumn = make_dataclass("AutoEvalColumn", auto_eval_column_dict, frozen=True)

@dataclass(frozen=True)
class EvalQueueColumn:  # Queue column
    model = ColumnContent("model", "markdown", True)
    revision = ColumnContent("revision", "str", True)
    private = ColumnContent("private", "bool", True)
    precision = ColumnContent("precision", "str", True)
    weight_type = ColumnContent("weight_type", "str", "Original")
    status = ColumnContent("status", "str", True)


baseline_row = {
    AutoEvalColumn.model.name: "<p>Baseline</p>",
    AutoEvalColumn.revision.name: "N/A",
    AutoEvalColumn.precision.name: None,
    AutoEvalColumn.average.name: 31.0,
    AutoEvalColumn.arc.name: 25.0,
    AutoEvalColumn.hellaswag.name: 25.0,
    AutoEvalColumn.mmlu.name: 25.0,
    AutoEvalColumn.truthfulqa.name: 25.0,
    AutoEvalColumn.winogrande.name: 50.0,
    AutoEvalColumn.gsm8k.name: 0.21,
    AutoEvalColumn.drop.name: 0.47,
    AutoEvalColumn.dummy.name: "baseline",
    AutoEvalColumn.model_type.name: "",
}

# Average ⬆️ human baseline is 0.897 (source: averaging human baselines below)
# ARC human baseline is 0.80 (source: https://lab42.global/arc/)
# HellaSwag human baseline is 0.95 (source: https://deepgram.com/learn/hellaswag-llm-benchmark-guide)
# MMLU human baseline is 0.898 (source: https://openreview.net/forum?id=d7KBjmI3GmQ)
# TruthfulQA human baseline is 0.94(source: https://arxiv.org/pdf/2109.07958.pdf)
# Drop: https://leaderboard.allenai.org/drop/submissions/public
# Winogrande: https://leaderboard.allenai.org/winogrande/submissions/public
# GSM8K: paper
# Define the human baselines
human_baseline_row = {
    AutoEvalColumn.model.name: "<p>Human performance</p>",
    AutoEvalColumn.revision.name: "N/A",
    AutoEvalColumn.precision.name: None,
    AutoEvalColumn.average.name: 92.75,
    AutoEvalColumn.arc.name: 80.0,
    AutoEvalColumn.hellaswag.name: 95.0,
    AutoEvalColumn.mmlu.name: 89.8,
    AutoEvalColumn.truthfulqa.name: 94.0,
    AutoEvalColumn.winogrande.name: 94.0,
    AutoEvalColumn.gsm8k.name: 100,
    AutoEvalColumn.drop.name: 96.42,
    AutoEvalColumn.dummy.name: "human_baseline",
    AutoEvalColumn.model_type.name: "",
}

@dataclass
class ModelDetails:
    name: str
    symbol: str = "" # emoji, only for the model type


class ModelType(Enum):
    PT = ModelDetails(name="pretrained", symbol="🟢")
    FT = ModelDetails(name="fine-tuned", symbol="🔶")
    IFT = ModelDetails(name="instruction-tuned", symbol="⭕")
    RL = ModelDetails(name="RL-tuned", symbol="🟦")
    Unknown = ModelDetails(name="", symbol="?")

    def to_str(self, separator=" "):
        return f"{self.value.symbol}{separator}{self.value.name}"

    @staticmethod
    def from_str(type):
        if "fine-tuned" in type or "🔶" in type:
            return ModelType.FT
        if "pretrained" in type or "🟢" in type:
            return ModelType.PT
        if "RL-tuned" in type or "🟦" in type:
            return ModelType.RL
        if "instruction-tuned" in type or "⭕" in type:
            return ModelType.IFT
        return ModelType.Unknown

class WeightType(Enum):
    Adapter = ModelDetails("Adapter")
    Original = ModelDetails("Original")
    Delta = ModelDetails("Delta")

class Precision(Enum):
    float16 = ModelDetails("float16")
    bfloat16 = ModelDetails("bfloat16")
    qt_8bit = ModelDetails("8bit")
    qt_4bit = ModelDetails("4bit")
    qt_GPTQ = ModelDetails("GPTQ")
    Unknown = ModelDetails("?")

    def from_str(precision):
        if precision in ["torch.float16", "float16"]:
            return Precision.float16
        if precision in ["torch.bfloat16", "bfloat16"]:
            return Precision.bfloat16
        if precision in ["8bit"]:
            return Precision.qt_8bit
        if precision in ["4bit"]:
            return Precision.qt_4bit
        if precision in ["GPTQ", "None"]:
            return Precision.qt_GPTQ
        return Precision.Unknown
        



# Column selection
COLS = [c.name for c in fields(AutoEvalColumn) if not c.hidden]
TYPES = [c.type for c in fields(AutoEvalColumn) if not c.hidden]
COLS_LITE = [c.name for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.hidden]
TYPES_LITE = [c.type for c in fields(AutoEvalColumn) if c.displayed_by_default and not c.hidden]

EVAL_COLS = [c.name for c in fields(EvalQueueColumn)]
EVAL_TYPES = [c.type for c in fields(EvalQueueColumn)]

BENCHMARK_COLS = [t.value.col_name for t in Tasks]

NUMERIC_INTERVALS = {
    "?": pd.Interval(-1, 0, closed="right"),
    "~1.5": pd.Interval(0, 2, closed="right"),
    "~3": pd.Interval(2, 4, closed="right"),
    "~7": pd.Interval(4, 9, closed="right"),
    "~13": pd.Interval(9, 20, closed="right"),
    "~35": pd.Interval(20, 45, closed="right"),
    "~60": pd.Interval(45, 70, closed="right"),
    "70+": pd.Interval(70, 10000, closed="right"),
}
