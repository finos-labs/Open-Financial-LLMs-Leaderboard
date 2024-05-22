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


NUM_FEWSHOT = 0  # Change with your few shot
# ---------------------------------------------------


# Your leaderboard name
TITLE = """<h1 align="center" id="space-title">🐲 Open Finance LLM Leaderboard</h1>"""

# What does your leaderboard evaluate?
INTRODUCTION_TEXT = """
🌟 The FinBen FLARE Leaderboard: Evaluate and compare the performance of financial Large Language Models (LLMs).

When you submit a model on the "Submit here!" page, it is automatically evaluated on a set of financial benchmarks.

The GPU used for evaluation is operated with the support of __[Wuhan University](http://en.whu.edu.cn/)__ and __[University of Florida](https://www.ufl.edu/)__.

The datasets used for evaluation consist of diverse financial datasets from `FinBen` benchmark to assess tasks such as sentiment analysis, named entity recognition, question answering, and more.

More details about the benchmarks and the evaluation process are provided on the “About” page.
"""

# Which evaluations are you running? how can people reproduce what you have?
LLM_BENCHMARKS_TEXT = """
## Introduction

The **Open Financial LLMs Leaderboard (OFLL)** is meticulously designed to rigorously track, rank, and evaluate state-of-the-art models in financial Natural Language Understanding and Prediction. Our leaderboard not only covers standard NLP tasks but also incorporates financial prediction tasks such as stock movement and credit scoring, offering a comprehensive evaluation for real-world financial applications.

## Icons & Model Types

- 🟢 : pretrained or continuously pretrained
- 🔶 : fine-tuned on domain-specific datasets
- 💬 : chat models (RLHF, DPO, ORPO, ...)
- 🤝 : base merges and moerges

If the icon is "?", it indicates that there is insufficient information about the model. Please provide information about the model through an issue! 🤩

**Note 1**: We reserve the right to correct any incorrect tags/icons after manual verification to ensure the accuracy and reliability of the leaderboard.

**Note 2** ⚠️: Some models might be widely discussed as subjects of caution by the community, implying that users should exercise restraint when using them. Models that have used the evaluation set for training to achieve a high leaderboard ranking, among others, may be selected as subjects of caution and might result in their deletion from the leaderboard.

## How It Works

📈 We evaluate models using Pixiu, a powerful and straightforward framework to test and assess language models on a large number of different evaluation tasks from FinBen, using datasets validated by financial experts.

### Evaluation Metrics

Our evaluation metrics include, but are not limited to, Accuracy, F1 Score, ROUGE score, BERTScore, and Matthews correlation coefficient (MCC), providing a multidimensional assessment of model performance. Metrics for specific tasks are as follows:

- **FPB**: F1
- **FiQA-SA**: F1
- **TSA**: RMSE
- **Headlines**: AvgF1
- **FOMC**: F1
- **FinArg-ACC**: MicroF1
- **FinArg-ARC**: MicroF1
- **Multifin**: MicroF1
- **MA**: MicroF1
- **MLESG**: MicroF1
- **NER**: EntityF1
- **FINER-ORD**: EntityF1
- **FinRED**: F1
- **SC**: F1
- **CD**: F1
- **FinQA**: EmAcc
- **TATQA**: EmAcc
- **ConvFinQA**: EmAcc
- **FNXL**: EntityF1
- **FSRL**: EntityF1
- **EDTSUM**: Rouge-1
- **ECTSUM**: Rouge-1
- **BigData22**: Acc
- **ACL18**: Acc
- **CIKM18**: Acc
- **German**: F1
- **Australian**: F1
- **LendingClub**: F1
- **ccf**: F1
- **ccfraud**: F1
- **polish**: F1
- **taiwan**: F1
- **portoseguro**: F1
- **travelinsurance**: F1

To ensure a fair and unbiased assessment of the models' true capabilities, all evaluations are conducted in zero-shot settings (0-shots). This approach eliminates any potential advantage from task-specific fine-tuning, providing a clear indication of how well the models can generalize to new tasks.

Given the nature of the tasks, which include multiple-choice and yes/no questions, we extract options from the generated text to evaluate performance.

Please, consider reaching out to us through the discussions tab if you are working on benchmarks for financial LLMs and willing to see them on this leaderboard as well. Your benchmark might change the whole game for financial models!

GPUs are provided by Wuhan University and the University of Florida for the evaluations.

## Details and Logs

- Detailed numerical results in the [results FinBen dataset](https://huggingface.co/datasets/FinBen/results)
- Community queries and running status in the [requests FinBen dataset](https://huggingface.co/datasets/FinBen/requests)

## More Resources

If you still have questions, you can check our github repository [here](https://github.com/The-FinAI/PIXIU).
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
@misc{xie2024finben,
          title={The FinBen: An Holistic Financial Benchmark for Large Language Models},
          author={Qianqian Xie and Weiguang Han and Zhengyu Chen and Ruoyu Xiang and Xiao Zhang and Yueru He and Mengxi Xiao and Dong Li and Yongfu Dai and Duanyu Feng and Yijing Xu and Haoqiang Kang and Ziyan Kuang and Chenhan Yuan and Kailai Yang and Zheheng Luo and Tianlin Zhang and Zhiwei Liu and Guojun Xiong and Zhiyang Deng and Yuechen Jiang and Zhiyuan Yao and Haohang Li and Yangyang Yu and Gang Hu and Jiajia Huang and Xiao-Yang Liu and Alejandro Lopez-Lira and Benyou Wang and Yanzhao Lai and Hao Wang and Min Peng and Sophia Ananiadou and Jimin Huang},
          year={2024},
          eprint={2402.12659},
          archivePrefix={arXiv},
          primaryClass={cs.CL}
        }
"""
