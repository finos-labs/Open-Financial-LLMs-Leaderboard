import os
import shutil
import numpy as np
import gradio as gr
from huggingface_hub import Repository, HfApi
from transformers import AutoConfig, AutoModel
import json
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import datetime
import glob
from dataclasses import dataclass
from typing import List, Tuple, Dict
# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)
LMEH_REPO = "HuggingFaceH4/lmeh_evaluations"

METRICS = ["acc_norm", "acc_norm", "acc_norm", "mc2"]
BENCHMARKS = ["arc_challenge", "hellaswag", "hendrycks", "truthfulqa_mc"]
BENCH_TO_NAME = {
    "arc_challenge":"ARC (25-shot) ⬆️",
     "hellaswag":"HellaSwag (10-shot) ⬆️",
     "hendrycks":"MMLU (5-shot) ⬆️",
     "truthfulqa_mc":"TruthQA (0-shot) ⬆️",
}
def make_clickable_model(model_name):        
    # remove user from model name
    #model_name_show = ' '.join(model_name.split('/')[1:])

    link = "https://huggingface.co/" + model_name
    return f'<a target="_blank" href="{link}" style="color: blue; text-decoration: underline;text-decoration-style: dotted;">{model_name}</a>'

@dataclass
class EvalResult:
    eval_name : str
    org : str
    model : str
    revision : str
    is_8bit : bool
    results : dict
    
    def to_dict(self):
        
        if self.org is not None:
            base_model =f"{self.org}/{self.model}"
        else:
            base_model =f"{self.model}"
        data_dict = {}
        
        data_dict["eval_name"] = self.eval_name
        data_dict["8bit"] = self.is_8bit
        data_dict["base_model"] = make_clickable_model(base_model)
        data_dict["revision"] = self.revision
        data_dict["total ⬆️"] = round(sum([v for k,v in self.results.items()])/4.0,1) 
        #data_dict["# params"] = get_n_params(base_model)
        
        for benchmark in BENCHMARKS:
            if not benchmark in self.results.keys():
                self.results[benchmark] = None
                
        for k,v in BENCH_TO_NAME.items():
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
    if len(path_split)== 7:
        # handles gpt2 type models that don't have an org
        result_key = f"{path_split[-4]}_{path_split[-3]}_{path_split[-2]}"
    else:
        result_key = f"{path_split[-5]}_{path_split[-4]}_{path_split[-3]}_{path_split[-2]}"
        org = path_split[-5]
        
    eval_result = None
    for benchmark, metric  in zip(BENCHMARKS, METRICS):
        if benchmark in json_filepath:
            accs = np.array([v[metric] for k, v in data["results"].items()])
            mean_acc = round(np.mean(accs)*100.0,1)
            eval_result = EvalResult(result_key, org, model, revision, is_8bit, {benchmark:mean_acc})
        
    return result_key, eval_result
        
    
    
   
def get_eval_results(is_public) -> List[EvalResult]:
    json_filepaths = glob.glob("evals/eval_results/public/**/16bit/*.json", recursive=True)
    if not is_public:
        json_filepaths += glob.glob("evals/eval_results/private/**/*.json", recursive=True)
        json_filepaths += glob.glob("evals/eval_results/private/**/*.json", recursive=True)
        json_filepaths += glob.glob("evals/eval_results/public/**/8bit/*.json", recursive=True) # include the 8bit evals of public models
    eval_results = {}
    
    for json_filepath in json_filepaths:
        result_key, eval_result = parse_eval_result(json_filepath)
        if result_key in eval_results.keys():
            eval_results[result_key].results.update(eval_result.results)
        else:
            eval_results[result_key] = eval_result
        
        
    eval_results = [v for k,v in eval_results.items()]
    
    return eval_results
    
def get_eval_results_dicts(is_public=True) -> List[Dict]:
    eval_results = get_eval_results(is_public)
    
    return [e.to_dict() for e in eval_results]

eval_results_dict = get_eval_results_dicts()
print(eval_results_dict)