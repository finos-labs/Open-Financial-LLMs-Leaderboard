from dataclasses import dataclass
from enum import Enum


@dataclass
class Task:
    benchmark: str
    metric: str
    col_name: str
    category: str


# Select your tasks here
# ---------------------------------------------------
class Tasks(Enum):
    task0 = Task("FPB", "F1", "FPB", category="Textual Analysis (TA)")
    task2 = Task("FiQA-SA", "F1", "FiQA-SA", category="Textual Analysis (TA)")
    task3 = Task("TSA", "RMSE", "TSA", category="Textual Analysis (TA)")
    task4 = Task("Headlines", "AvgF1", "Headlines", category="Textual Analysis (TA)")
    task5 = Task("FOMC", "F1", "FOMC", category="Textual Analysis (TA)")
    task7 = Task("FinArg-ACC", "MicroF1", "FinArg-ACC", category="Textual Analysis (TA)")
    task8 = Task("FinArg-ARC", "MicroF1", "FinArg-ARC", category="Textual Analysis (TA)")
    task9 = Task("MultiFin", "MicroF1", "MultiFin", category="Textual Analysis (TA)")
    task10 = Task("MA", "MicroF1", "MA", category="Textual Analysis (TA)")
    task11 = Task("MLESG", "MicroF1", "MLESG", category="Textual Analysis (TA)")
    task12 = Task("NER", "EntityF1", "NER", category="Information Extraction (IE)")
    task13 = Task("FINER-ORD", "EntityF1", "FINER-ORD", category="Information Extraction (IE)")
    task14 = Task("FinRED", "F1", "FinRED", category="Information Extraction (IE)")
    task15 = Task("SC", "F1", "SC", category="Information Extraction (IE)")
    task16 = Task("CD", "F1", "CD", category="Information Extraction (IE)")
    task17 = Task("FinQA", "EmAcc", "FinQA", category="Question Answering (QA)")
    task18 = Task("TATQA", "EmAcc", "TATQA", category="Question Answering (QA)")
    task19 = Task("ConvFinQA", "EmAcc", "ConvFinQA", category="Question Answering (QA)")
    task20 = Task("FNXL", "EntityF1", "FNXL", category="Information Extraction (IE)")
    task21 = Task("FSRL", "EntityF1", "FSRL", category="Information Extraction (IE)")
    task22 = Task("EDTSUM", "Rouge-1", "EDTSUM", category="Text Generation (TG)")
    task25 = Task("ECTSUM", "Rouge-1", "ECTSUM", category="Text Generation (TG)")
    task28 = Task("BigData22", "Acc", "BigData22", category="Forecasting (FO)")
    task30 = Task("ACL18", "Acc", "ACL18", category="Forecasting (FO)")
    task32 = Task("CIKM18", "Acc", "CIKM18", category="Forecasting (FO)")
    task34 = Task("German", "MCC", "German", category="Risk Management (RM)")
    task36 = Task("Australian", "MCC", "Australian", category="Risk Management (RM)")
    task38 = Task("LendingClub", "MCC", "LendingClub", category="Risk Management (RM)")
    task40 = Task("ccf", "MCC", "ccf", category="Risk Management (RM)")
    task42 = Task("ccfraud", "MCC", "ccfraud", category="Risk Management (RM)")
    task44 = Task("polish", "MCC", "polish", category="Risk Management (RM)")
    task46 = Task("taiwan", "MCC", "taiwan", category="Risk Management (RM)")
    task48 = Task("portoseguro", "MCC", "portoseguro", category="Risk Management (RM)")
    task50 = Task("travelinsurance", "MCC", "travelinsurance", category="Risk Management (RM)")
    task51 = Task("MultiFin-ES", "F1", "MultiFin-ES", category="Spanish")
    task52 = Task("EFP", "F1", "EFP", category="Spanish")
    task53 = Task("EFPA", "F1", "EFPA", category="Spanish")
    task54 = Task("FinanceES", "F1", "FinanceES", category="Spanish")
    task55 = Task("TSA-Spanish", "F1", "TSA-Spanish", category="Spanish")
    task56 = Task("FinTrade", "SR", "FinTrade", category="Decision-Making (DM)")

NUM_FEWSHOT = 0  # Change with your few shot
# ---------------------------------------------------


# Your leaderboard name
TITLE = """<h1 align="center" id="space-title">🐲 Open Financial LLM Leaderboard</h1>"""

# What does your leaderboard evaluate?
INTRODUCTION_TEXT = """
🌟 The Open Financial LLM Leaderboard: Evaluate and compare the performance of financial Large Language Models (LLMs).

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

- **FPB**: F1, Accuracy. Financial PhraseBank classification task. This dataset is from the Financial PhraseBank, containing annotated phrases used in financial contexts. The classification task involves determining sentiment (positive, negative, neutral) for each phrase, essential for understanding financial news and reports.
- **FiQA-SA**: F1. Sentiment analysis on FiQA financial domain. Derived from the FiQA dataset, this task focuses on sentiment analysis in the financial domain, particularly within news and social media. The dataset is crucial for gauging market sentiment based on financial communications.
- **TSA**: F1, RMSE. Sentiment analysis on social media. The TSA dataset is utilized to analyze sentiment from tweets related to financial markets. The dataset is essential for real-time sentiment analysis, providing insights into market trends influenced by public opinion.
- **Headlines**: AvgF1. News headline classification. This dataset consists of financial news headlines, with each headline categorized into various financial events or sentiment classes. The task challenges models to understand and classify brief, context-rich text segments that drive market movements.
- **FOMC**: F1, Accuracy. Hawkish-dovish classification. Derived from transcripts of the Federal Open Market Committee (FOMC) meetings, this dataset involves classifying statements as hawkish or dovish, which indicates the stance of monetary policy. Accurate classification helps predict market reactions to central bank communications.
- **FinArg-ACC**: F1, Accuracy. Financial argument unit classification. This dataset involves the classification of argument units in financial documents, such as identifying the main claim, supporting evidence, or counterarguments. The task is crucial for automated financial document analysis, enabling the extraction of structured information from unstructured text.
- **FinArg-ARC**: F1, Accuracy. Financial argument relation classification. This task focuses on classifying relationships between different argument units within financial texts, such as support, opposition, or neutrality. Understanding these relations is critical for constructing coherent financial narratives from fragmented data.
- **MultiFin**: F1, Accuracy. Multi-class financial sentiment analysis. The MultiFin dataset includes diverse financial texts requiring sentiment classification across multiple categories, such as bullish, bearish, or neutral. The task is pivotal for analyzing sentiment in financial markets from varied sources like reports, news articles, and social media.
- **MA**: F1, Accuracy. Deal completeness classification. The dataset revolves around classifying mergers and acquisitions (M&A) reports to determine whether a deal has been completed. The task helps in tracking and analyzing the outcomes of corporate transactions, which is key for investment decisions.
- **MLESG**: F1, Accuracy. ESG issue identification. This dataset focuses on identifying Environmental, Social, and Governance (ESG) issues within financial texts. Models are evaluated on their ability to correctly classify and categorize ESG-related content, which is increasingly important for responsible investing.
- **NER**: EntityF1. Named entity recognition in financial texts. This task involves identifying and classifying named entities (e.g., companies, financial instruments, persons) within financial documents. Accurate NER is crucial for information extraction and financial analysis automation.
- **FINER-ORD**: EntityF1. Ordinal classification in financial NER. This dataset extends standard NER by requiring models to classify entities not just by type but also by their ordinal relevance (e.g., primary, secondary importance) within the text. This is useful for prioritizing information in financial summaries.
- **FinRED**: F1, EntityF1. Financial relation extraction from text. The task involves extracting relationships between financial entities, such as ownership, acquisition, or partnership relations. This is important for building knowledge graphs and conducting in-depth financial analysis.
- **SC**: F1, EntityF1. Causal classification task in the financial domain. The dataset requires models to classify causal relationships in financial texts, such as determining whether one event causes another. Understanding causality is critical for risk assessment and decision-making in finance.
- **CD**: F1, EntityF1. Causal detection. Similar to SC, but focused on detecting causality in a broader range of financial texts, including reports, news, and social media. The task evaluates the model's ability to identify causal links, which are key drivers in financial analysis.
- **FinQA**: EmAcc. Numerical question answering in finance. FinQA involves answering numerical questions based on financial documents, such as balance sheets or income statements. The task tests a model's ability to perform calculations or identify numerical data in a text.
- **TATQA**: F1, EmAcc. Table-based question answering in financial documents. This task is centered around answering questions that require interpreting and extracting information from tables in financial documents. It's crucial for automating the analysis of structured financial data.
- **ConvFinQA**: EmAcc. Multi-turn question answering in finance. ConvFinQA extends standard QA tasks by requiring models to handle multi-turn dialogues, where each question builds on the previous one. This simulates real-world scenarios where financial analysts ask a series of related questions.
- **FNXL**: F1, EmAcc. Numeric labeling in financial texts. This dataset requires models to label numeric values within financial documents, categorizing them by type (e.g., revenue, profit) and relevance. It tests the model's ability to understand the role of numbers in financial contexts.
- **FSRL**: F1, EmAcc. Financial statement relation linking. The task involves linking related information across different financial statements, such as matching revenue figures from income statements with corresponding cash flow data. This is key for comprehensive financial analysis.
- **EDTSUM**: ROUGE, BERTScore, BARTScore. Extractive document summarization in finance. The dataset involves summarizing lengthy financial documents by extracting the most relevant sentences. This task evaluates a model's ability to generate concise summaries that retain critical information.
- **ECTSUM**: ROUGE, BERTScore, BARTScore. Extractive content summarization. Similar to EDTSUM, but with a broader focus on summarizing content from various financial document types, including reports, articles, and regulatory filings.
- **BigData22**: Accuracy, MCC. Stock movement prediction. This dataset is used for predicting stock price movements based on financial news and reports. The task evaluates a model's ability to forecast market trends, which is essential for investment strategies.
- **ACL18**: Accuracy, MCC. Financial news-based stock prediction. The ACL18 dataset focuses on predicting stock movements specifically using news headlines and articles. It's a benchmark for evaluating the impact of news on stock prices.
- **CIKM18**: Accuracy, MCC. Financial market prediction using news. This task involves predicting broader market movements, such as indices, based on financial news. It tests the model's ability to aggregate and interpret multiple sources of financial information.
- **German**: F1, MCC. Credit scoring in the German market. The dataset includes data on loan applicants in Germany, with the task being to predict creditworthiness. This is important for financial institutions in assessing loan risks.
- **Australian**: F1, MCC. Credit scoring in the Australian market. Similar to the German dataset, but tailored for the Australian financial context, this task evaluates the model's ability to predict credit risk in this specific market.
- **LendingClub**: F1, MCC. Peer-to-peer lending risk prediction. This dataset involves predicting the risk of default for loans issued through the LendingClub platform, which is a major peer-to-peer lending service. The task is crucial for risk management in alternative finance.
- **ccf**: F1, MCC. Credit card fraud detection. The dataset is used to identify fraudulent transactions within a large dataset of credit card operations. Accurate detection is critical for financial security and fraud prevention.
- **ccfraud**: F1, MCC. Credit card transaction fraud detection. Similar to the ccf dataset but focusing on transaction-level analysis, this task evaluates the model's ability to detect anomalies that indicate fraud.
- **polish**: F1, MCC. Credit risk prediction in the Polish market. This task involves predicting the likelihood of default for loan applicants in Poland, with the dataset tailored to local economic and financial conditions.
- **taiwan**: F1, MCC. Credit risk prediction in the Taiwanese market. Similar to the Polish dataset but focused on Taiwan, this task evaluates the model's ability to assess credit risk in this market.
- **portoseguro**: F1, MCC. Claim analysis in the Brazilian market. The dataset involves predicting insurance claim risks in Brazil, specifically for auto insurance. The task tests the model's ability to assess and manage insurance risks.
- **travelinsurance**: F1, MCC. Travel insurance claim prediction. This dataset is used for predicting the likelihood of a travel insurance claim being made, which is important for risk pricing and policy management in the travel insurance industry.
- **MultiFin-ES**: F1. Multi-class financial sentiment analysis in Spanish. This dataset is used to analyze sentiment in Spanish-language financial texts. It evaluates the model's ability to handle sentiment classification across multiple categories in a non-English context.
- **EFP**: F1. Financial phrase classification in Spanish. Similar to the FPB dataset but in Spanish, this task involves classifying financial phrases according to sentiment or intent, specifically for Spanish-language content.
- **EFPA**: F1. Financial argument classification in Spanish. This dataset requires the classification of arguments in Spanish financial documents, focusing on identifying claims, evidence, and other argumentative structures.
- **FinanceES**: F1. Financial sentiment classification in Spanish. The task involves classifying sentiment in a broad range of Spanish financial documents, including news articles and reports. It tests the model's ability to adapt sentiment analysis techniques to a non-English language.
- **TSA-Spanish**: F1. Sentiment analysis in Spanish. This dataset involves sentiment analysis on Spanish-language tweets and short texts, similar to the English TSA dataset but tailored for Spanish speakers. It evaluates the model's ability to process and analyze sentiment in social media content.
- **FinTrade**: SR. Stock trading dataset. FinTrade is a novel dataset developed specifically for evaluating stock trading tasks using LLMs. It incorporates historical stock prices, financial news, and sentiment data from 10 different stocks over a year. This dataset is designed to simulate real-world trading scenarios, allowing models to perform agent-based financial trading. The task evaluates the models on multiple financial metrics such as Cumulative Return (CR), Sharpe Ratio (SR), Daily Volatility (DV), Annualized Volatility (AV), and Maximum Drawdown (MD). These metrics provide a comprehensive assessment of the model's profitability, risk management, and decision-making capabilities.



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
@article{Xie2024FinBen,
  title={FinBen: A Holistic Financial Benchmark for Large Language Models},
  author={Qianqian Xie and Weiguang Han and Zhengyu Chen and Ruoyu Xiang and Xiao Zhang and Yueru He and Mengxi Xiao and Dong Li and Yongfu Dai and Duanyu Feng and Yijing Xu and Haoqiang Kang and Ziyan Kuang and Chenhan Yuan and Kailai Yang and Zheheng Luo and Tianlin Zhang and Zhiwei Liu and Guojun Xiong and Zhiyang Deng and Yuechen Jiang and Zhiyuan Yao and Haohang Li and Yangyang Yu and Gang Hu and Jiajia Huang and Xiao-Yang Liu and Alejandro Lopez-Lira and Benyou Wang and Yanzhao Lai and Hao Wang and Min Peng and Sophia Ananiadou and Jimin Huang},
  journal={NeurIPS, Special Track on Datasets and Benchmarks},
  year={2024},
}
"""
