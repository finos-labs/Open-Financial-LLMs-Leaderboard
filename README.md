---
title: Demo Leaderboard
emoji: 🥇
colorFrom: green
colorTo: indigo
sdk: gradio
sdk_version: 4.4.0
app_file: app.py
pinned: true
license: apache-2.0
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

Most of the variables to change for a default leaderboard are in src/env (replace the path for your leaderboard) and src/about.

Results files should have the following format:
```
{
    "config": {
        "model_dtype": "torch.float16", # or torch.bfloat16 or 8bit or 4bit
        "model_name": "path of the model on the hub: org/model",
        "model_sha": "revision on the hub",
    },
    "results": {
        "task_name": {
            "metric_name": score,
        },
        "task_name2": {
            "metric_name": score,
        }
    }
}
```

Request files are created automatically by this tool.

If you encounter problem on the space, don't hesitate to restart it to remove the create eval-queue, eval-queue-bk, eval-results and eval-results-bk created folder.

