import glob
import json
from dataclasses import dataclass
from typing import Optional

from huggingface_hub import HfApi, snapshot_download
from src.envs import TOKEN

@dataclass
class EvalRequest:
    model: str
    private: bool
    status: str
    json_filepath: str
    weight_type: str = "Original"
    model_type: str = ""  # pretrained, finetuned, with RL
    precision: str = ""  # float16, bfloat16
    base_model: Optional[str] = None # for adapter models
    revision: str = "main" # commit
    submitted_time: Optional[str] = "2022-05-18T11:40:22.519222"  # random date just so that we can still order requests by date
    model_type: Optional[str] = None
    likes: Optional[int] = 0
    params: Optional[int] = None
    license: Optional[str] = ""
    
    def get_model_args(self):
        model_args = f"pretrained={self.model},revision={self.revision}"

        if self.precision in ["float16", "bfloat16", "float32"]:
            model_args += f",dtype={self.precision}"
        # Quantized models need some added config, the install of bits and bytes, etc
        #elif self.precision == "8bit":
        #    model_args += ",load_in_8bit=True"
        #elif self.precision == "4bit":
        #    model_args += ",load_in_4bit=True"
        #elif self.precision == "GPTQ":
            # A GPTQ model does not need dtype to be specified,
            # it will be inferred from the config
            pass
        else:
            raise Exception(f"Unknown precision {self.precision}.")
        
        return model_args


def set_eval_request(api: HfApi, eval_request: EvalRequest, set_to_status: str, hf_repo: str, local_dir: str):
    """Updates a given eval request with its new status on the hub (running, completed, failed, ...)"""
    json_filepath = eval_request.json_filepath

    with open(json_filepath) as fp:
        data = json.load(fp)

    data["status"] = set_to_status

    with open(json_filepath, "w") as f:
        f.write(json.dumps(data))

    api.upload_file(
        path_or_fileobj=json_filepath,
        path_in_repo=json_filepath.replace(local_dir, ""),
        repo_id=hf_repo,
        repo_type="dataset",
    )


def get_eval_requests(job_status: list, local_dir: str, hf_repo: str) -> list[EvalRequest]:
    """Get all pending evaluation requests and return a list in which private
    models appearing first, followed by public models sorted by the number of
    likes.

    Returns:
        `list[EvalRequest]`: a list of model info dicts.
    """
    snapshot_download(repo_id=hf_repo, revision="main", local_dir=local_dir, repo_type="dataset", max_workers=60, token=TOKEN)
    json_files = glob.glob(f"{local_dir}/**/*.json", recursive=True)

    eval_requests = []
    for json_filepath in json_files:
        with open(json_filepath) as fp:
            data = json.load(fp)
        if data["status"] in job_status:
            data["json_filepath"] = json_filepath
            eval_request = EvalRequest(**data)
            eval_requests.append(eval_request)

    return eval_requests


def check_completed_evals(
    api: HfApi,
    hf_repo: str,
    local_dir: str,
    checked_status: str,
    completed_status: str,
    failed_status: str,
    hf_repo_results: str,
    local_dir_results: str,
):
    """Checks if the currently running evals are completed, if yes, update their status on the hub."""
    snapshot_download(repo_id=hf_repo_results, revision="main", local_dir=local_dir_results, repo_type="dataset", max_workers=60, token=TOKEN)

    running_evals = get_eval_requests(checked_status, hf_repo=hf_repo, local_dir=local_dir)

    for eval_request in running_evals:
        model = eval_request.model
        print("====================================")
        print(f"Checking {model}")

        output_path = model
        output_file = f"{local_dir_results}/{output_path}/results*.json"
        output_file_exists = len(glob.glob(output_file)) > 0

        if output_file_exists:
            print(
                f"EXISTS output file exists for {model} setting it to {completed_status}"
            )
            set_eval_request(api, eval_request, completed_status, hf_repo, local_dir)
        else:
            print(
                f"No result file found for {model} setting it to {failed_status}"
            )
            set_eval_request(api, eval_request, failed_status, hf_repo, local_dir)
