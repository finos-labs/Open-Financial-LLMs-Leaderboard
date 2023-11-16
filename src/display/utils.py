from dataclasses import dataclass
from enum import Enum

import pandas as pd


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


def fields(raw_class):
    return [v for k, v in raw_class.__dict__.items() if k[:2] != "__" and k[-2:] != "__"]


@dataclass(frozen=True)
class AutoEvalColumn:  # Auto evals column
    model_type_symbol = ColumnContent("T", "str", True, never_hidden=True)
    model = ColumnContent("Model", "markdown", True, never_hidden=True)
    average = ColumnContent("Average ⬆️", "number", True)
    arc = ColumnContent("ARC", "number", True)
    hellaswag = ColumnContent("HellaSwag", "number", True)
    mmlu = ColumnContent("MMLU", "number", True)
    truthfulqa = ColumnContent("TruthfulQA", "number", True)
    winogrande = ColumnContent("Winogrande", "number", True)
    gsm8k = ColumnContent("GSM8K", "number", True)
    drop = ColumnContent("DROP", "number", True)
    model_type = ColumnContent("Type", "str", False)
    architecture = ColumnContent("Architecture", "str", False)
    weight_type = ColumnContent("Weight type", "str", False, True)
    precision = ColumnContent("Precision", "str", False)  # , True)
    license = ColumnContent("Hub License", "str", False)
    params = ColumnContent("#Params (B)", "number", False)
    likes = ColumnContent("Hub ❤️", "number", False)
    still_on_hub = ColumnContent("Available on the hub", "bool", False)
    revision = ColumnContent("Model sha", "str", False, False)
    dummy = ColumnContent(
        "model_name_for_query", "str", False, dummy=True
    )  # dummy col to implement search bar (hidden by custom CSS)


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
class ModelTypeDetails:
    name: str
    symbol: str  # emoji


class ModelType(Enum):
    PT = ModelTypeDetails(name="pretrained", symbol="🟢")
    FT = ModelTypeDetails(name="fine-tuned", symbol="🔶")
    IFT = ModelTypeDetails(name="instruction-tuned", symbol="⭕")
    RL = ModelTypeDetails(name="RL-tuned", symbol="🟦")
    Unknown = ModelTypeDetails(name="", symbol="?")

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


@dataclass
class Task:
    benchmark: str
    metric: str
    col_name: str


class Tasks(Enum):
    arc = Task("arc:challenge", "acc_norm", AutoEvalColumn.arc.name)
    hellaswag = Task("hellaswag", "acc_norm", AutoEvalColumn.hellaswag.name)
    mmlu = Task("hendrycksTest", "acc", AutoEvalColumn.mmlu.name)
    truthfulqa = Task("truthfulqa:mc", "mc2", AutoEvalColumn.truthfulqa.name)
    winogrande = Task("winogrande", "acc", AutoEvalColumn.winogrande.name)
    gsm8k = Task("gsm8k", "acc", AutoEvalColumn.gsm8k.name)
    drop = Task("drop", "f1", AutoEvalColumn.drop.name)


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
