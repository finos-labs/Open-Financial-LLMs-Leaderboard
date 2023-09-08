import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import dateutil
import numpy as np

from src.display_models.utils import AutoEvalColumn, make_clickable_model

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
    precision: str = ""
    model_type: str = ""
    weight_type: str = ""
    date: str = ""

    def to_dict(self):
        from src.load_from_hub import is_model_on_hub

        if self.org is not None:
            base_model = f"{self.org}/{self.model}"
        else:
            base_model = f"{self.model}"
        data_dict = {}

        data_dict["eval_name"] = self.eval_name  # not a column, just a save name
        data_dict["weight_type"] = self.weight_type  # not a column, just a save name
        data_dict[AutoEvalColumn.precision.name] = self.precision
        data_dict[AutoEvalColumn.model_type.name] = self.model_type
        data_dict[AutoEvalColumn.model.name] = make_clickable_model(base_model)
        data_dict[AutoEvalColumn.dummy.name] = base_model
        data_dict[AutoEvalColumn.revision.name] = self.revision
        data_dict[AutoEvalColumn.average.name] = sum([v for k, v in self.results.items()]) / 4.0
        data_dict[AutoEvalColumn.still_on_hub.name] = (
            is_model_on_hub(base_model, self.revision)[0] or base_model == "baseline"
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
            return None, []  # we skip models with the wrong version

    try:
        config = data["config"]
    except KeyError:
        config = data["config_general"]
    model = config.get("model_name", None)
    if model is None:
        model = config.get("model_args", None)

    model_sha = config.get("model_sha", "")
    model_split = model.split("/", 1)

    precision = config.get("model_dtype")

    model = model_split[-1]

    if len(model_split) == 1:
        org = None
        model = model_split[0]
        result_key = f"{model}_{precision}"
    else:
        org = model_split[0]
        model = model_split[1]
        result_key = f"{org}_{model}_{precision}"

    eval_results = []
    for benchmark, metric in zip(BENCHMARKS, METRICS):
        accs = np.array([v.get(metric, None) for k, v in data["results"].items() if benchmark in k])
        if accs.size == 0 or any([acc is None for acc in accs]):
            continue
        mean_acc = np.mean(accs) * 100.0
        eval_results.append(
            EvalResult(
                eval_name=result_key,
                org=org,
                model=model,
                revision=model_sha,
                results={benchmark: mean_acc},
                precision=precision,  # todo model_type=, weight_type=
                date=config.get("submission_date")
            )
        )

    return result_key, eval_results


def get_eval_results() -> List[EvalResult]:
    json_filepaths = []

    for root, dir, files in os.walk("eval-results"):
        # We should only have json files in model results
        if len(files) == 0 or any([not f.endswith(".json") for f in files]):
            continue

        # Sort the files by date
        # store results by precision maybe?
        try:
            files.sort(key=lambda x: x.removesuffix(".json").removeprefix("results_")[:-7])
        except dateutil.parser._parser.ParserError:
            files = [files[-1]]

        # up_to_date = files[-1]
        for file in files:
            json_filepaths.append(os.path.join(root, file))

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


def get_eval_results_dicts() -> List[Dict]:
    eval_results = get_eval_results()

    return [e.to_dict() for e in eval_results]
