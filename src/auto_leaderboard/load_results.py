from dataclasses import dataclass

import glob
import json
from typing import Dict, List, Tuple

from src.utils_display import AutoEvalColumn, make_clickable_model
import numpy as np

# clone / pull the lmeh eval data
METRICS = ["acc_norm", "acc_norm", "acc_norm", "mc2"]
BENCHMARKS = ["arc_challenge", "hellaswag", "hendrycks", "truthfulqa_mc"]
BENCH_TO_NAME = {
    "arc_challenge": AutoEvalColumn.arc.name,
    "hellaswag": AutoEvalColumn.hellaswag.name,
    "hendrycks": AutoEvalColumn.mmlu.name,
    "truthfulqa_mc": AutoEvalColumn.truthfulqa.name,
}


@dataclass
class EvalResult:
    eval_name: str
    org: str
    model: str
    revision: str
    is_8bit: bool
    results: dict

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
            if not benchmark in self.results.keys():
                self.results[benchmark] = None

        for k, v in BENCH_TO_NAME.items():
            data_dict[v] = self.results[k]

        return data_dict


def parse_eval_result(json_filepath: str) -> Tuple[str, dict]:
    with open(json_filepath) as fp:
        data = json.load(fp)

    path_split = json_filepath.split("/")
    org = None
    model = path_split[-4]
    is_8bit = path_split[-2] == "8bit"
    revision = path_split[-3]
    if len(path_split) == 7:
        # handles gpt2 type models that don't have an org
        result_key = f"{model}_{revision}_{is_8bit}"
    else:
        org = path_split[-5]
        result_key =  f"{org}_{model}_{revision}_{is_8bit}"

    eval_result = None
    for benchmark, metric in zip(BENCHMARKS, METRICS):
        if benchmark in json_filepath:
            accs = np.array([v[metric] for v in data["results"].values()])
            mean_acc = round(np.mean(accs) * 100.0, 1)
            eval_result = EvalResult(
                result_key, org, model, revision, is_8bit, {benchmark: mean_acc}
            )

    return result_key, eval_result


def get_eval_results(is_public) -> List[EvalResult]:
    json_filepaths = glob.glob(
        "auto_evals/eval_results/public/**/16bit/*.json", recursive=True
    )
    if not is_public:
        json_filepaths += glob.glob(
            "auto_evals/eval_results/private/**/*.json", recursive=True
        )
        json_filepaths += glob.glob(
            "auto_evals/eval_results/private/**/*.json", recursive=True
        )
        # include the 8bit evals of public models
        json_filepaths += glob.glob(
            "auto_evals/eval_results/public/**/8bit/*.json", recursive=True
        )  
    eval_results = {}

    for json_filepath in json_filepaths:
        result_key, eval_result = parse_eval_result(json_filepath)
        if result_key in eval_results.keys():
            eval_results[result_key].results.update(eval_result.results)
        else:
            eval_results[result_key] = eval_result

    eval_results = [v for v in eval_results.values()]

    return eval_results


def get_eval_results_dicts(is_public=True) -> List[Dict]:
    eval_results = get_eval_results(is_public)

    return [e.to_dict() for e in eval_results]
