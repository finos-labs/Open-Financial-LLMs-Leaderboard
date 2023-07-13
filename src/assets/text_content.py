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

Other cool benchmarks for LLMs are developped at HuggingFace, go check them out: 🙋🤖 [human and GPT4 evals](https://huggingface.co/spaces/HuggingFaceH4/human_eval_llm_leaderboard), 🖥️ [performance benchmarks](https://huggingface.co/spaces/optimum/llm-perf-leaderboard)
"""

LLM_BENCHMARKS_TEXT = f"""
# Context
With the plethora of large language models (LLMs) and chatbots being released week upon week, often with grandiose claims of their performance, it can be hard to filter out the genuine progress that is being made by the open-source community and which model is the current state of the art. 

📈 We evaluate models on 4 key benchmarks from the <a href="https://github.com/EleutherAI/lm-evaluation-harness" target="_blank">  Eleuther AI Language Model Evaluation Harness </a>, a unified framework to test generative language models on a large number of different evaluation tasks. 

- <a href="https://arxiv.org/abs/1803.05457" target="_blank">  AI2 Reasoning Challenge </a> (25-shot) - a set of grade-school science questions.
- <a href="https://arxiv.org/abs/1905.07830" target="_blank">  HellaSwag </a> (10-shot) - a test of commonsense inference, which is easy for humans (~95%) but challenging for SOTA models.
- <a href="https://arxiv.org/abs/2009.03300" target="_blank">  MMLU </a>  (5-shot) - a test to measure a text model's multitask accuracy. The test covers 57 tasks including elementary mathematics, US history, computer science, law, and more.
- <a href="https://arxiv.org/abs/2109.07958" target="_blank">  TruthfulQA </a> (0-shot) - a test to measure a model’s propensity to reproduce falsehoods commonly found online.

We chose these benchmarks as they test a variety of reasoning and general knowledge across a wide variety of fields in 0-shot and few-shot settings.


# Some good practices before submitting a model

## 1) Make sure you can load your model and tokenizer using AutoClasses:
```python
from transformers import AutoConfig, AutoModel, AutoTokenizer
config = AutoConfig.from_pretrained("your model name", revision=revision)
model = AutoModel.from_pretrained("your model name", revision=revision)
tokenizer = AutoTokenizer.from_pretrained("your model name", revision=revision)
```
If this step fails, follow the error messages to debug your model before submitting it. It's likely your model has been improperly uploaded. 

Note: make sure your model is public!
Note: if your model needs `use_remote_code=True`, we do not support this option yet but we are working on adding it, stay posted!

## 2) Convert your model weights to [safetensors](https://huggingface.co/docs/safetensors/index)
It's a new format for storing weights which is safer and faster to load and use. It will also allow us to add the number of weights of your model to the `Extended Viewer`!

## 3) Make sure your model has an open license!
This is a leaderboard for Open LLMs, and we'd love for as many people as possible to know they can use your model 🤗

## 4) Fill up your model card
When we add extra information about models to the leaderboard, it will be automatically taken from the model card

# Reproduction
To reproduce our results, here is the commands you can run, using [this version](https://github.com/EleutherAI/lm-evaluation-harness/tree/e47e01beea79cfe87421e2dac49e64d499c240b4) of the Eleuther AI Harness:
`python main.py --model=hf-causal --model_args="pretrained=<your_model>,use_accelerate=True,revision=<your_model_revision>"`
` --tasks=<task_list> --num_fewshot=<n_few_shot> --batch_size=2 --output_path=<output_path>`

The total batch size we get for models which fit on one A100 node is 16 (8 GPUs * 2). If you don't use parallelism, adapt your batch size to fit. 
*You can expect results to vary slightly for different batch sizes because of padding.*

The tasks and few shots parameters are:
- ARC: 25-shot, *arc-challenge* (`acc_norm`)
- HellaSwag: 10-shot, *hellaswag* (`acc_norm`)
- TruthfulQA: 0-shot, *truthfulqa-mc* (`mc2`)
- MMLU: 5-shot, *hendrycksTest-abstract_algebra,hendrycksTest-anatomy,hendrycksTest-astronomy,hendrycksTest-business_ethics,hendrycksTest-clinical_knowledge,hendrycksTest-college_biology,hendrycksTest-college_chemistry,hendrycksTest-college_computer_science,hendrycksTest-college_mathematics,hendrycksTest-college_medicine,hendrycksTest-college_physics,hendrycksTest-computer_security,hendrycksTest-conceptual_physics,hendrycksTest-econometrics,hendrycksTest-electrical_engineering,hendrycksTest-elementary_mathematics,hendrycksTest-formal_logic,hendrycksTest-global_facts,hendrycksTest-high_school_biology,hendrycksTest-high_school_chemistry,hendrycksTest-high_school_computer_science,hendrycksTest-high_school_european_history,hendrycksTest-high_school_geography,hendrycksTest-high_school_government_and_politics,hendrycksTest-high_school_macroeconomics,hendrycksTest-high_school_mathematics,hendrycksTest-high_school_microeconomics,hendrycksTest-high_school_physics,hendrycksTest-high_school_psychology,hendrycksTest-high_school_statistics,hendrycksTest-high_school_us_history,hendrycksTest-high_school_world_history,hendrycksTest-human_aging,hendrycksTest-human_sexuality,hendrycksTest-international_law,hendrycksTest-jurisprudence,hendrycksTest-logical_fallacies,hendrycksTest-machine_learning,hendrycksTest-management,hendrycksTest-marketing,hendrycksTest-medical_genetics,hendrycksTest-miscellaneous,hendrycksTest-moral_disputes,hendrycksTest-moral_scenarios,hendrycksTest-nutrition,hendrycksTest-philosophy,hendrycksTest-prehistory,hendrycksTest-professional_accounting,hendrycksTest-professional_law,hendrycksTest-professional_medicine,hendrycksTest-professional_psychology,hendrycksTest-public_relations,hendrycksTest-security_studies,hendrycksTest-sociology,hendrycksTest-us_foreign_policy,hendrycksTest-virology,hendrycksTest-world_religions* (`acc` of `all`)

# In case of model failure
If your model is displayed in the `FAILED` category, its execution stopped. 
Make sure you have followed the above steps first. 
If everything is done, check you can launch the EleutherAIHarness on your model locally, using the above command without modifications (you can add `--limit` to limit the number of examples per task).


"""

EVALUATION_QUEUE_TEXT = f"""
# Evaluation Queue for the 🤗 Open LLM Leaderboard
These models will be automatically evaluated on the 🤗 cluster.
"""

CITATION_BUTTON_LABEL = "Copy the following snippet to cite these results"
CITATION_BUTTON_TEXT = r"""@misc{open-llm-leaderboard,
  author = {Edward Beeching, Clémentine Fourrier, Nathan Habib, Sheon Han, Nathan Lambert, Nazneen Rajani, Omar Sanseviero, Lewis Tunstall, Thomas Wolf},
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