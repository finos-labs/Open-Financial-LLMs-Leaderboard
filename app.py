import os
import shutil
import numpy as np
import gradio as gr
from huggingface_hub import Repository
import json
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)
repo=None
if H4_TOKEN:
    # try:
    #     shutil.rmtree("./evals/")
    # except:
    #     pass

    repo = Repository(
        local_dir="./evals/", clone_from="HuggingFaceH4/lmeh_evaluations", use_auth_token=H4_TOKEN, repo_type="dataset"
    )
    repo.git_pull()


# parse the results
BENCHMARKS = ["arc_challenge", "hellaswag", "hendrycks", "truthfulqa_mc"]
BENCH_TO_NAME = {
    "arc_challenge":"ARC",
     "hellaswag":"HellaSwag",
     "hendrycks":"MMLU",
     "truthfulqa_mc":"TruthQA",
}
METRICS = ["acc_norm", "acc_norm", "acc_norm", "mc2"]

entries = [entry for entry in os.listdir("evals") if not entry.startswith('.')]
model_directories = [entry for entry in entries if os.path.isdir(os.path.join("evals", entry))]


def make_clickable_model(model_name):
    # remove user from model name
    #model_name_show = ' '.join(model_name.split('/')[1:])

    link = "https://huggingface.co/" + model_name
    return f'<a target="_blank" href="{link}" style="color: blue; text-decoration: underline;text-decoration-style: dotted;">{model_name}</a>'

def load_results(model, benchmark, metric):
    file_path = os.path.join("evals", model, f"{model}-eval_{benchmark}.json")
    if not os.path.exists(file_path):
        return 0.0, None

    with open(file_path) as fp:
        data = json.load(fp)
    accs = np.array([v[metric] for k, v in data["results"].items()])
    mean_acc = np.mean(accs)  
    return mean_acc, data["config"]["model_args"]

COLS = ["eval_name", "total", "ARC", "HellaSwag", "MMLU", "TruthQA", "base_model"]
TYPES = ["str", "number", "number", "number", "number", "number","markdown", ]
def get_leaderboard():
    if repo: 
        repo.git_pull()
    all_data = []
    for model in model_directories:
        model_data = {"base_model": None}
        model_data = {"eval_name": model}
        
        for benchmark, metric in zip(BENCHMARKS, METRICS):
            value, base_model = load_results(model, benchmark, metric)        
            model_data[BENCH_TO_NAME[benchmark]] = value
            if base_model is not None: # in case the last benchmark failed
                model_data["base_model"] = base_model
            
        model_data["total"] = sum(model_data[benchmark] for benchmark in BENCH_TO_NAME.values())
        
        if model_data["base_model"] is not None:
            model_data["base_model"] = make_clickable_model(model_data["base_model"])
        all_data.append(model_data)
        
    dataframe = pd.DataFrame.from_records(all_data)
    dataframe = dataframe.sort_values(by=['total'], ascending=False)
    
    dataframe = dataframe[COLS]
    return dataframe

leaderboard = get_leaderboard()

block = gr.Blocks()
with block: 
    gr.Markdown(f"""
    # H4 Model Evaluation leaderboard using the <a href="https://github.com/EleutherAI/lm-evaluation-harness" target="_blank"> LMEH benchmark suite </a>. 
    Evaluation is performed against 4 popular benchmarks AI2 Reasoning Challenge, HellaSwag, MMLU, and TruthFul QC MC. To run your own benchmarks, refer to the README in the H4 repo.
    """)
    
    with gr.Row():
        leaderboard_table = gr.components.Dataframe(value=leaderboard, headers=COLS,
                                                    datatype=TYPES, max_rows=5)
    with gr.Row():
        refresh_button = gr.Button("Refresh")
        refresh_button.click(get_leaderboard, inputs=[], outputs=leaderboard_table) 
    
    
    
block.launch()

def refresh_leaderboard():
    leaderboard_table = get_leaderboard()
    print("leaderboard updated")

scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_leaderboard, trigger="interval", seconds=300) # refresh every 5 mins
scheduler.start()