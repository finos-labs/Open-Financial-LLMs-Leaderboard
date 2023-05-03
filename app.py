import os
import shutil
import numpy as np
import gradio as gr
from huggingface_hub import Repository, HfApi
from transformers import AutoConfig
import json
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import datetime
from utils import get_eval_results_dicts, make_clickable_model, get_n_params

# clone / pull the lmeh eval data
H4_TOKEN = os.environ.get("H4_TOKEN", None)
LMEH_REPO = "HuggingFaceH4/lmeh_evaluations"

repo=None
if H4_TOKEN:
    print("pulling repo")
    # try:
    #     shutil.rmtree("./evals/")
    # except:
    #     pass

    repo = Repository(
        local_dir="./evals/", clone_from=LMEH_REPO, use_auth_token=H4_TOKEN, repo_type="dataset"
    )
    repo.git_pull()


# parse the results
BENCHMARKS = ["arc_challenge", "hellaswag", "hendrycks", "truthfulqa_mc"]

METRICS = ["acc_norm", "acc_norm", "acc_norm", "mc2"]


def load_results(model, benchmark, metric):
    file_path = os.path.join("evals", model, f"{model}-eval_{benchmark}.json")
    if not os.path.exists(file_path):
        return 0.0, None

    with open(file_path) as fp:
        data = json.load(fp)
    accs = np.array([v[metric] for k, v in data["results"].items()])
    mean_acc = np.mean(accs)  
    return mean_acc, data["config"]["model_args"]


COLS = ["base_model", "revision", "8bit", "total ⬆️", "ARC (25-shot) ⬆️", "HellaSwag (10-shot) ⬆️", "MMLU (5-shot) ⬆️", "TruthQA (0-shot) ⬆️"]
TYPES = ["markdown","str", "bool", "number", "number", "number", "number", "number", ]

EVAL_COLS = ["model", "revision", "private", "8bit_eval", "is_delta_weight", "status"]
EVAL_TYPES = ["markdown","str", "bool", "bool", "bool", "str"]
def get_leaderboard():
    if repo: 
        print("pulling changes")
        repo.git_pull()
        
    all_data = get_eval_results_dicts()
    dataframe = pd.DataFrame.from_records(all_data)
    dataframe = dataframe.sort_values(by=['total ⬆️'], ascending=False)
    print(dataframe)
    dataframe = dataframe[COLS]
    return dataframe

def get_eval_table():
    if repo: 
        print("pulling changes for eval")
        repo.git_pull()
    entries = [entry for entry in os.listdir("evals/eval_requests") if not entry.startswith('.')] 
    all_evals = []
    
    for entry in entries:
        print(entry)
        if ".json"in entry:
            file_path = os.path.join("evals/eval_requests", entry)
            with open(file_path) as fp:
                data = json.load(fp)
                
            data["# params"] = get_n_params(data["model"])
            data["model"] = make_clickable_model(data["model"])
            data["revision"] = data.get("revision", "main")
            

            all_evals.append(data)
        else:
            # this is a folder
            sub_entries = [e for e in os.listdir(f"evals/eval_requests/{entry}") if not e.startswith('.')] 
            for sub_entry in sub_entries:
                file_path = os.path.join("evals/eval_requests", entry, sub_entry)
                with open(file_path) as fp:
                    data = json.load(fp)
                    
                #data["# params"] = get_n_params(data["model"])
                data["model"] = make_clickable_model(data["model"])
                all_evals.append(data)

    
    dataframe = pd.DataFrame.from_records(all_evals)
    return dataframe[EVAL_COLS]


leaderboard = get_leaderboard()
eval_queue = get_eval_table()

def is_model_on_hub(model_name, revision) -> bool:
    try:
        config = AutoConfig.from_pretrained(model_name, revision=revision)
        return True
        
    except Exception as e:
        print("Could not get the model config from the hub")
        print(e)
        return False
        


def add_new_eval(model:str, base_model : str, revision:str, is_8_bit_eval: bool, private:bool, is_delta_weight:bool):
    # check the model actually exists before adding the eval
    if revision == "":
        revision = "main"
    if is_delta_weight and not is_model_on_hub(base_model, revision):
        print(base_model, "base model not found on hub")
        return
    
    if not is_model_on_hub(model, revision):
        print(model, "not found on hub")
        return
    print("adding new eval")
    
    eval_entry = {
        "model" : model,
        "base_model" : base_model,
        "revision" : revision,
        "private" : private,
        "8bit_eval" : is_8_bit_eval,
        "is_delta_weight" : is_delta_weight,
        "status" : "PENDING"
    }    
    
    user_name = ""
    model_path = model
    if "/" in model:
        user_name = model.split("/")[0]
        model_path = model.split("/")[1]
    
    OUT_DIR=f"eval_requests/{user_name}"
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = f"{OUT_DIR}/{model_path}_eval_request_{private}_{is_8_bit_eval}_{is_delta_weight}.json"
    
    with open(out_path, "w") as f:
        f.write(json.dumps(eval_entry))
    LMEH_REPO = "HuggingFaceH4/lmeh_evaluations"
    
    api = HfApi()
    api.upload_file(
        path_or_fileobj=out_path,
        path_in_repo=out_path,
        repo_id=LMEH_REPO,
        token=H4_TOKEN,
        repo_type="dataset",
    )

    
def refresh():
    return get_leaderboard(), get_eval_table()
    


block = gr.Blocks()
with block: 
    with gr.Row():
        gr.Markdown(f"""
        # 🤗 H4 Model Evaluation leaderboard using the <a href="https://github.com/EleutherAI/lm-evaluation-harness" target="_blank"> LMEH benchmark suite </a>. 
        Evaluation is performed against 4 popular benchmarks AI2 Reasoning Challenge, HellaSwag, MMLU, and TruthFul QC MC. To run your own benchmarks, refer to the README in the H4 repo.
        """)
    
    with gr.Row():
        leaderboard_table = gr.components.Dataframe(value=leaderboard, headers=COLS,
                                                    datatype=TYPES, max_rows=5)

    
    
    with gr.Row():
        gr.Markdown(f"""
    # Evaluation Queue for the LMEH benchmarks, these models will be automatically evaluated on the 🤗 cluster
    
    """)
    
    with gr.Row():
        eval_table = gr.components.Dataframe(value=eval_queue, headers=EVAL_COLS,
                                                    datatype=EVAL_TYPES, max_rows=5)    
        
    with gr.Row():
        refresh_button = gr.Button("Refresh")
        refresh_button.click(refresh, inputs=[], outputs=[leaderboard_table, eval_table]) 
        
    with gr.Accordion("Submit a new model for evaluation"):
        # with gr.Row():
        #     gr.Markdown(f"""# Submit a new model for evaluation""")
        with gr.Row():
            with gr.Column():
                model_name_textbox = gr.Textbox(label="Model name")
                revision_name_textbox = gr.Textbox(label="revision", placeholder="main")
                base_model_name_textbox = gr.Textbox(label="base model (for delta)")
            with gr.Column():
                is_8bit_toggle = gr.Checkbox(False, label="8 bit eval")
                private = gr.Checkbox(False, label="Private")
                is_delta_weight = gr.Checkbox(False, label="Delta weights")
            
        with gr.Row():
            submit_button = gr.Button("Submit Eval")
            submit_button.click(add_new_eval, [model_name_textbox, base_model_name_textbox, revision_name_textbox, is_8bit_toggle, private, is_delta_weight])
        
        
        
    


print("adding refresh leaderboard")
def refresh_leaderboard():
    leaderboard_table = get_leaderboard()
    print("leaderboard updated")

scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_leaderboard, trigger="interval", seconds=300) # refresh every 5 mins
scheduler.start()

block.launch()