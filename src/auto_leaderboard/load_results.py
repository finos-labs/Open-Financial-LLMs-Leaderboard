from dataclasses import dataclass

import glob
import json
from typing import Dict, List, Tuple

from src.utils_display import AutoEvalColumn, make_clickable_model
import numpy as np

METRICS = ["acc_norm", "acc_norm", "acc", "mc2"]
BENCHMARKS = ["arc:challenge", "hellaswag", "hendrycksTest", "truthfulqa:mc"]
BENCH_TO_NAME = {
    "arc:challenge": AutoEvalColumn.arc.name,
    "hellaswag": AutoEvalColumn.hellaswag.name,
    "hendrycksTest": AutoEvalColumn.mmlu.name,
    "truthfulqa:mc": AutoEvalColumn.truthfulqa.name,
}


@dataclass
class EvalResult:
    eval_name: str
    org: str
    model: str
    revision: str
    results: dict
    is_8bit: bool = False

    def to_dict(self):
        if self.org is not None:
            base_model = f"{self.org}/{self.model}"
        else:
            base_model = f"{self.model}"
        data_dict = {}

        data_dict["eval_name"] = self.eval_name # not a column, just a save name
        data_dict[AutoEvalColumn.is_8bit.name] = self.is_8bit
        data_dict[AutoEvalColumn.model.name] = make_clickable_model(base_model)
        data_dict[AutoEvalColumn.dummy.name] = base_model
        data_dict[AutoEvalColumn.revision.name] = self.revision
        data_dict[AutoEvalColumn.average.name] = round(
            sum([v for k, v in self.results.items()]) / 4.0, 1
        )

        for benchmark in BENCHMARKS:
            if benchmark not in self.results.keys():
                self.results[benchmark] = None

        for k, v in BENCH_TO_NAME.items():
            data_dict[v] = self.results[k]

        return data_dict


def parse_eval_result(json_filepath: str) -> Tuple[str, list[dict]]:
    with open(json_filepath) as fp:
        data = json.load(fp)
    
    for mmlu_k in ["harness|hendrycksTest-abstract_algebra|5", "hendrycksTest-abstract_algebra"]:
        if mmlu_k in data["versions"] and data["versions"][mmlu_k] == 0:
            return None, [] # we skip models with the wrong version 

    config = data["config"]
    model = config.get("model_name", None)
    if model is None:
        model = config.get("model_args", None)

    model_sha = config.get("model_sha", "")
    eval_sha = config.get("lighteval_sha", "")
    model_split = model.split("/", 1)

    model = model_split[-1]

    if len(model_split) == 1:
        org = None
        model = model_split[0]
        result_key = f"{model}_{model_sha}_{eval_sha}"
    else:
        org = model_split[0]
        model = model_split[1]
        result_key =  f"{org}_{model}_{model_sha}_{eval_sha}"

    eval_results = []
    for benchmark, metric in zip(BENCHMARKS, METRICS):
        accs = np.array([v[metric] for k, v in data["results"].items() if benchmark in k])
        if accs.size == 0:
            continue
        mean_acc = round(np.mean(accs) * 100.0, 1)
        eval_results.append(EvalResult(
            result_key, org, model, model_sha, {benchmark: mean_acc}
        ))

    return result_key, eval_results


def get_eval_results(is_public) -> List[EvalResult]:
    json_filepaths = glob.glob(
        "eval-results/**/results*.json", recursive=True
    )
    if not is_public:
        json_filepaths += glob.glob(
            "private-eval-results/**/results*.json", recursive=True
        )

    eval_results = {}

    for json_filepath in json_filepaths:
        result_key, results = parse_eval_result(json_filepath)
        for eval_result in results:
            if result_key in eval_results.keys():
                eval_results[result_key].results.update(eval_result.results)
            else:
                eval_results[result_key] = eval_result

    eval_results = [v for v in eval_results.values()]

    return eval_results


def get_eval_results_dicts(is_public=True) -> List[Dict]:
    eval_results = get_eval_results(is_public)

    return [e.to_dict() for e in eval_results]
