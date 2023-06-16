from src.utils_display import AutoEvalColumn, model_hyperlink

gpt4_values = {
    AutoEvalColumn.model.name: model_hyperlink("https://arxiv.org/abs/2303.08774", "gpt4"),
    AutoEvalColumn.revision.name: "tech report",
    AutoEvalColumn.is_8bit.name: None,
    AutoEvalColumn.average.name: 84.3,
    AutoEvalColumn.arc.name: 96.3,
    AutoEvalColumn.hellaswag.name:  95.3,
    AutoEvalColumn.mmlu.name:  86.4,
    AutoEvalColumn.truthfulqa.name:  59.0,
    AutoEvalColumn.dummy.name: "GPT-4",
}

gpt35_values = {
    AutoEvalColumn.model.name: model_hyperlink("https://arxiv.org/abs/2303.08774", "gpt3.5"),
    AutoEvalColumn.revision.name: "tech report",
    AutoEvalColumn.is_8bit.name: None,
    AutoEvalColumn.average.name: 71.9,
    AutoEvalColumn.arc.name: 85.2,
    AutoEvalColumn.hellaswag.name:  85.5,
    AutoEvalColumn.mmlu.name:  70.0,
    AutoEvalColumn.truthfulqa.name:  47.0,
    AutoEvalColumn.dummy.name: "GPT-3.5",
}

baseline = {
    AutoEvalColumn.model.name: "<p>Baseline</p>",
    AutoEvalColumn.revision.name: "N/A",
    AutoEvalColumn.is_8bit.name: None,
    AutoEvalColumn.average.name: 25.0,
    AutoEvalColumn.arc.name: 25.0,
    AutoEvalColumn.hellaswag.name:  25.0,
    AutoEvalColumn.mmlu.name:  25.0,
    AutoEvalColumn.truthfulqa.name:  25.0,
    AutoEvalColumn.dummy.name: "baseline",
}

