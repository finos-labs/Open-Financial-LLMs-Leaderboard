CHANGELOG_TEXT = f"""
## [2023-05-30] 
- Add a citation button
- Simplify Gradio layout

## [2023-05-29] 
- Auto-restart every hour for the latest results
- Sync with the internal version (minor style changes)

## [2023-05-24] 
- Add a baseline that has 25.0 for all values
- Add CHANGELOG

## [2023-05-23] 
- Fix a CSS issue that made the leaderboard hard to read in dark mode

## [2023-05-22] 
- Display a success/error message after submitting evaluation requests
- Reject duplicate submission
- Do not display results that have incomplete results 
- Display different queues for jobs that are RUNNING, PENDING, FINISHED status 

## [2023-05-15] 
- Fix a typo: from "TruthQA" to "TruthfulQA"

## [2023-05-10] 
- Fix a bug that prevented auto-refresh

## [2023-05-10] 
- Release the leaderboard to public
"""

TITLE = """<h1 align="center" id="space-title">🤗 Open LLM Leaderboard</h1>"""

INTRODUCTION_TEXT = f"""
📐 With the plethora of large language models (LLMs) and chatbots being released week upon week, often with grandiose claims of their performance, it can be hard to filter out the genuine progress that is being made by the open-source community and which model is the current state of the art. The 🤗 Open LLM Leaderboard aims to track, rank and evaluate LLMs and chatbots as they are released. 

🤗 A key advantage of this leaderboard is that anyone from the community can submit a model for automated evaluation on the 🤗 GPU cluster, as long as it is a 🤗 Transformers model with weights on the Hub. We also support evaluation of models with delta-weights for non-commercial licensed models, such as LLaMa.

📈 In the **first tab (LLM Benchmarks)**, we evaluate models on 4 key benchmarks from the <a href="https://github.com/EleutherAI/lm-evaluation-harness" target="_blank">  Eleuther AI Language Model Evaluation Harness </a>, a unified framework to test generative language models on a large number of different evaluation tasks. In the **second tab (Human & GPT Evaluations)**, TK.

Evaluation is performed against 4 popular benchmarks:
- <a href="https://arxiv.org/abs/1803.05457" target="_blank">  AI2 Reasoning Challenge </a> (25-shot) - a set of grade-school science questions.
- <a href="https://arxiv.org/abs/1905.07830" target="_blank">  HellaSwag </a> (10-shot) - a test of commonsense inference, which is easy for humans (~95%) but challenging for SOTA models.
- <a href="https://arxiv.org/abs/2009.03300" target="_blank">  MMLU </a>  (5-shot) - a test to measure a text model's multitask accuracy. The test covers 57 tasks including elementary mathematics, US history, computer science, law, and more.
- <a href="https://arxiv.org/abs/2109.07958" target="_blank">  TruthfulQA </a> (0-shot) - a benchmark to measure whether a language model is truthful in generating answers to questions.

We chose these benchmarks as they test a variety of reasoning and general knowledge across a wide variety of fields in 0-shot and few-shot settings.
"""

EVALUATION_QUEUE_TEXT = f"""
# Evaluation Queue for the 🤗 Open LLM Leaderboard, these models will be automatically evaluated on the 🤗 cluster
"""

CITATION_BUTTON_LABEL = "Copy the following snippet to cite these results"
CITATION_BUTTON_TEXT = r"""@misc{open-llm-leaderboard,
  author = {Edward Beeching, Sheon Han, Nathan Lambert, Nazneen Rajani, Omar Sanseviero, Lewis Tunstall, Thomas Wolf},
  title = {Open LLM Leaderboard},
  year = {2023},
  publisher = {Hugging Face},
  howpublished = "\url{https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard}"

}"""

