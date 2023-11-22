"""This file should be used after pip install -r requirements.
It creates a folder not ported during harness package creation (as they don't use a Manifest file atm and it ignore `.json` files).
It will need to be updated if we want to use the harness' version of big bench to actually copy the json files.
"""
import os

import lm_eval

if __name__ == "__main__":
    lm_eval_path = lm_eval.__path__[0]
    os.makedirs(os.path.join(lm_eval_path, "datasets", "bigbench_resources"), exist_ok=True)