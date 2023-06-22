CHANGELOG_TEXT = f"""
## [2023-06-19]
- Added model type column
- Hid revision and 8bit columns since all models are the same atm

## [2023-06-16]
- Refactored code base
- Added new columns: number of parameters, hub likes, license

## [2023-06-13] 
- Adjust description for TruthfulQA

## [2023-06-12] 
- Add Human & GPT-4 Evaluations

## [2023-06-05] 
- Increase concurrent thread count to 40
- Search models on ENTER

## [2023-06-02] 
- Add a typeahead search bar
- Use webhooks to automatically spawn a new Space when someone opens a PR
- Start recording `submitted_time` for eval requests
- Limit AutoEvalColumn max-width

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
- Fix a typo: from "TruthQA" to "QA"

## [2023-05-10] 
- Fix a bug that prevented auto-refresh

## [2023-05-10] 
- Release the leaderboard to public
"""

TITLE = """<h1 align="center" id="space-title">🤗 Open LLM Leaderboard</h1>"""

INTRODUCTION_TEXT = f"""
📐 The 🤗 Open LLM Leaderboard aims to track, rank and evaluate LLMs and chatbots as they are released. 

🤗 Anyone from the community can submit a model for automated evaluation on the 🤗 GPU cluster, as long as it is a 🤗 Transformers model with weights on the Hub. We also support evaluation of models with delta-weights for non-commercial licensed models, such as LLaMa.
"""

LLM_BENCHMARKS_TEXT = f"""
With the plethora of large language models (LLMs) and chatbots being released week upon week, often with grandiose claims of their performance, it can be hard to filter out the genuine progress that is being made by the open-source community and which model is the current state of the art. 

📈 We evaluate models on 4 key benchmarks from the <a href="https://github.com/EleutherAI/lm-evaluation-harness" target="_blank">  Eleuther AI Language Model Evaluation Harness </a>, a unified framework to test generative language models on a large number of different evaluation tasks. 

- <a href="https://arxiv.org/abs/1803.05457" target="_blank">  AI2 Reasoning Challenge </a> (25-shot) - a set of grade-school science questions.
- <a href="https://arxiv.org/abs/1905.07830" target="_blank">  HellaSwag </a> (10-shot) - a test of commonsense inference, which is easy for humans (~95%) but challenging for SOTA models.
- <a href="https://arxiv.org/abs/2009.03300" target="_blank">  MMLU </a>  (5-shot) - a test to measure a text model's multitask accuracy. The test covers 57 tasks including elementary mathematics, US history, computer science, law, and more.
- <a href="https://arxiv.org/abs/2109.07958" target="_blank">  TruthfulQA </a> (0-shot) - a test to measure a model’s propensity to reproduce falsehoods commonly found online.

We chose these benchmarks as they test a variety of reasoning and general knowledge across a wide variety of fields in 0-shot and few-shot settings.
"""

EVALUATION_QUEUE_TEXT = f"""
# Evaluation Queue for the 🤗 Open LLM Leaderboard
These models will be automatically evaluated on the 🤗 cluster.
"""

CITATION_BUTTON_LABEL = "Copy the following snippet to cite these results"
CITATION_BUTTON_TEXT = r"""@misc{open-llm-leaderboard,
  author = {Edward Beeching, Sheon Han, Nathan Lambert, Nazneen Rajani, Omar Sanseviero, Lewis Tunstall, Thomas Wolf},
  title = {Open LLM Leaderboard},
  year = {2023},
  publisher = {Hugging Face},
  howpublished = "\url{https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard}"

}
@software{eval-harness,
  author       = {Gao, Leo and
                  Tow, Jonathan and
                  Biderman, Stella and
                  Black, Sid and
                  DiPofi, Anthony and
                  Foster, Charles and
                  Golding, Laurence and
                  Hsu, Jeffrey and
                  McDonell, Kyle and
                  Muennighoff, Niklas and
                  Phang, Jason and
                  Reynolds, Laria and
                  Tang, Eric and
                  Thite, Anish and
                  Wang, Ben and
                  Wang, Kevin and
                  Zou, Andy},
  title        = {A framework for few-shot language model evaluation},
  month        = sep,
  year         = 2021,
  publisher    = {Zenodo},
  version      = {v0.0.1},
  doi          = {10.5281/zenodo.5371628},
  url          = {https://doi.org/10.5281/zenodo.5371628}
}
@misc{clark2018think,
      title={Think you have Solved Question Answering? Try ARC, the AI2 Reasoning Challenge}, 
      author={Peter Clark and Isaac Cowhey and Oren Etzioni and Tushar Khot and Ashish Sabharwal and Carissa Schoenick and Oyvind Tafjord},
      year={2018},
      eprint={1803.05457},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
@misc{zellers2019hellaswag,
      title={HellaSwag: Can a Machine Really Finish Your Sentence?}, 
      author={Rowan Zellers and Ari Holtzman and Yonatan Bisk and Ali Farhadi and Yejin Choi},
      year={2019},
      eprint={1905.07830},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
@misc{hendrycks2021measuring,
      title={Measuring Massive Multitask Language Understanding}, 
      author={Dan Hendrycks and Collin Burns and Steven Basart and Andy Zou and Mantas Mazeika and Dawn Song and Jacob Steinhardt},
      year={2021},
      eprint={2009.03300},
      archivePrefix={arXiv},
      primaryClass={cs.CY}
}
@misc{lin2022truthfulqa,
      title={TruthfulQA: Measuring How Models Mimic Human Falsehoods}, 
      author={Stephanie Lin and Jacob Hilton and Owain Evans},
      year={2022},
      eprint={2109.07958},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}"""