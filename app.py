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
from utils import get_eval_results_dicts, make_clickable_model

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

def get_n_params(base_model):
    
    # config = AutoConfig.from_pretrained(model_name)

    # # Retrieve the number of parameters from the configuration
    # try:
    #     num_params = config.n_parameters
    # except AttributeError:
    #     print(f"Error: The number of parameters is not available in the config for the model '{model_name}'.")
    #     return None

    # return num_params
    
    now = datetime.datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")
    return time_string

COLS = ["eval_name", "# params", "total ⬆️", "ARC (25-shot) ⬆️", "HellaSwag (10-shot) ⬆️", "MMLU (5-shot) ⬆️", "TruthQA (0-shot) ⬆️", "base_model"]
TYPES = ["str","str",  "number", "number", "number", "number", "number","markdown", ]

EVAL_COLS = ["model","# params", "private", "8bit_eval", "is_delta_weight", "status"]
EVAL_TYPES = ["markdown","str",  "bool", "bool", "bool", "str"]
def get_leaderboard():
    if repo: 
        print("pulling changes")
        repo.git_pull()
    # entries = [entry for entry in os.listdir("evals") if not (entry.startswith('.') or entry=="eval_requests" or entry=="evals")] 
    # model_directories = [entry for entry in entries if os.path.isdir(os.path.join("evals", entry))]
    # all_data = []
    # for model in model_directories:
    #     model_data = {"base_model": None, "eval_name": model}
        
    #     for benchmark, metric in zip(BENCHMARKS, METRICS):
    #         value, base_model = load_results(model, benchmark, metric)        
    #         model_data[BENCH_TO_NAME[benchmark]] = round(value,3)
    #         if base_model is not None: # in case the last benchmark failed
    #             model_data["base_model"] = base_model
            
    #     model_data["total ⬆️"] = round(sum(model_data[benchmark] for benchmark in BENCH_TO_NAME.values()),3)
        
    #     if model_data["base_model"] is not None:
    #         model_data["base_model"] = make_clickable_model(model_data["base_model"])
        
    #     model_data["# params"] = get_n_params(model_data["base_model"])
        
    #     if model_data["base_model"] is not None:
    #         all_data.append(model_data)
        
    all_data = get_eval_results_dicts()
    dataframe = pd.DataFrame.from_records(all_data)
    dataframe = dataframe.sort_values(by=['total ⬆️'], ascending=False)
    
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
            

            all_evals.append(data)
        else:
            # this is a folder
            sub_entries = [e for e in os.listdir(f"evals/eval_requests/{entry}") if not e.startswith('.')] 
            for sub_entry in sub_entries:
                file_path = os.path.join("evals/eval_requests", entry, sub_entry)
                with open(file_path) as fp:
                    data = json.load(fp)
                    
                data["# params"] = get_n_params(data["model"])
                data["model"] = make_clickable_model(data["model"])
                all_evals.append(data)

    
    dataframe = pd.DataFrame.from_records(all_evals)
    return dataframe[EVAL_COLS]


leaderboard = get_leaderboard()
eval_queue = get_eval_table()

def is_model_on_hub(model_name) -> bool:
    try:
        config = AutoConfig.from_pretrained(model_name)
        return True
        
    except Exception as e:
        print("Could not get the model config from the hub")
        print(e)
        return False
        


def add_new_eval(model:str, private:bool, is_8_bit_eval: bool, is_delta_weight:bool):
    # check the model actually exists before adding the eval
    if not is_model_on_hub(model):
        print(model, "not found on hub")
        return
    print("adding new eval")
    
    eval_entry = {
        "model" : model,
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
            model_name_textbox = gr.Textbox(label="model_name")
            is_8bit_toggle = gr.Checkbox(False, label="8 bit Eval?")
            private = gr.Checkbox(False, label="Private?")
            is_delta_weight = gr.Checkbox(False, label="Delta Weights?")
            
        with gr.Row():
            submit_button = gr.Button("Submit Eval")
            submit_button.click(add_new_eval, [model_name_textbox, is_8bit_toggle, private, is_delta_weight])
        
        
        
    


print("adding refresh leaderboard")
def refresh_leaderboard():
    leaderboard_table = get_leaderboard()
    print("leaderboard updated")

scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_leaderboard, trigger="interval", seconds=300) # refresh every 5 mins
scheduler.start()

block.launch()