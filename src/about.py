from dataclasses import dataclass
from enum import Enum

@dataclass
class Task:
    benchmark: str
    metric: str
    col_name: str


# Select your tasks here
# ---------------------------------------------------
class Tasks(Enum):
    # task_key in the json file, metric_key in the json file, name to display in the leaderboard 
    task0 = Task("FPB", "F1", "FPB")
    task2 = Task("FiQA-SA", "F1", "FiQA-SA")
    task3 = Task("TSA", "RMSE", "TSA")
    task4 = Task("Headlines", "AvgF1", "Headlines")
    task5 = Task("FOMC", "F1", "FOMC")
    task7 = Task("FinArg-ACC", "MicroF1", "FinArg-ACC")
    task8 = Task("FinArg-ARC", "MicroF1", "FinArg-ARC")
    task9 = Task("MultiFin", "MicroF1", "Multifin")
    task10 = Task("MA", "MicroF1", "MA")
    task11 = Task("MLESG", "MicroF1", "MLESG")
    task12 = Task("NER", "EntityF1", "NER")
    task13 = Task("FINER-ORD", "EntityF1", "FINER-ORD")
    task14 = Task("FinRED", "F1", "FinRED")
    task15 = Task("SC", "F1", "SC")
    task16 = Task("CD", "F1", "CD")
    task17 = Task("FinQA", "EmAcc", "FinQA")
    task18 = Task("TATQA", "EmAcc", "TATQA")
    task19 = Task("ConvFinQA", "EmAcc", "ConvFinQA")
    task20 = Task("FNXL", "EntityF1", "FNXL")
    task21 = Task("FSRL", "EntityF1", "FSRL")
    task22 = Task("EDTSUM", "Rouge-1", "EDTSUM")
    task25 = Task("ECTSUM", "Rouge-1", "ECTSUM")
    task28 = Task("BigData22", "Acc", "BigData22")
    task30 = Task("ACL18", "Acc", "ACL18")
    task32 = Task("CIKM18", "Acc", "CIKM18")
    task34 = Task("German", "F1", "German")
    task36 = Task("Australian", "F1", "Australian")
    task38 = Task("LendingClub", "F1", "LendingClub")
    task40 = Task("ccf", "F1", "ccf")
    task42 = Task("ccfraud", "F1", "ccfraud")
    task44 = Task("polish", "F1", "polish")
    task46 = Task("taiwan", "F1", "taiwan")
    task48 = Task("portoseguro", "F1", "portoseguro")
    task50 = Task("travelinsurance", "F1", "travelinsurance")

NUM_FEWSHOT = 0 # Change with your few shot
# ---------------------------------------------------



# Your leaderboard name
TITLE = """<h1 align="center" id="space-title">🐲 The FinBen FLARE Leaderboard</h1>"""

# What does your leaderboard evaluate?
INTRODUCTION_TEXT = """
"""

# Which evaluations are you running? how can people reproduce what you have?
LLM_BENCHMARKS_TEXT = f"""
## Introduction
📊 The FinBen FLARE Leaderboard is designed to rigorously track, rank, and evaluate state-of-the-art models in financial Natural Language Understanding and Prediction. 

📈 Unique to FLARE, our leaderboard not only covers standard NLP tasks but also incorporates financial prediction tasks such as stock movement and credit scoring, offering a more comprehensive evaluation for real-world financial applications.

## Metrics
📚 Our evaluation metrics include, but are not limited to, Accuracy, F1 Score, ROUGE score, BERTScore, and Matthews correlation coefficient (MCC), providing a multidimensional assessment of model performance.
   Metrics for specific tasks are as follows:
    FPB-F1
    FiQA-SA-F1
    TSA-RMSE
    Headlines-AvgF1
    FOMC-F1
    FinArg-ACC-MicroF1
    FinArg-ARC-MicroF1
    Multifin-MicroF1
    MA-MicroF1
    MLESG-MicroF1
    NER-EntityF1
    FINER-ORD-EntityF1
    FinRED-F1
    SC-F1
    CD-F1
    FinQA-EmAcc
    TATQA-EmAcc
    ConvFinQA-EmAcc
    FNXL-EntityF1
    FSRL-EntityF1
    EDTSUM-Rouge-1
    ECTSUM-Rouge-1
    BigData22-Acc
    ACL18-Acc
    CIKM18-Acc
    German-F1
    Australian-F1
    LendingClub-F1
    ccf-F1
    ccfraud-F1
    polish-F1
    taiwan-F1
    portoseguro-F1
    travelinsurance-F1
    
## REPRODUCIBILITY
🔗 For more details, refer to our GitHub page [here](https://github.com/The-FinAI/PIXIU).

"""

EVALUATION_QUEUE_TEXT = """
## Some good practices before submitting a model

### 1) Make sure you can load your model and tokenizer using AutoClasses:
```python
from transformers import AutoConfig, AutoModel, AutoTokenizer
config = AutoConfig.from_pretrained("your model name", revision=revision)
model = AutoModel.from_pretrained("your model name", revision=revision)
tokenizer = AutoTokenizer.from_pretrained("your model name", revision=revision)
```
If this step fails, follow the error messages to debug your model before submitting it. It's likely your model has been improperly uploaded.

Note: make sure your model is public!
Note: if your model needs `use_remote_code=True`, we do not support this option yet but we are working on adding it, stay posted!

### 2) Convert your model weights to [safetensors](https://huggingface.co/docs/safetensors/index)
It's a new format for storing weights which is safer and faster to load and use. It will also allow us to add the number of parameters of your model to the `Extended Viewer`!

### 3) Make sure your model has an open license!
This is a leaderboard for Open LLMs, and we'd love for as many people as possible to know they can use your model 🤗

### 4) Fill up your model card
When we add extra information about models to the leaderboard, it will be automatically taken from the model card

## In case of model failure
If your model is displayed in the `FAILED` category, its execution stopped.
Make sure you have followed the above steps first.
If everything is done, check you can launch the EleutherAIHarness on your model locally, using the above command without modifications (you can add `--limit` to limit the number of examples per task).
"""

CITATION_BUTTON_LABEL = "Copy the following snippet to cite these results"
CITATION_BUTTON_TEXT = r"""
"""
