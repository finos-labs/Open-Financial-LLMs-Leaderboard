from datasets import load_dataset

ds = load_dataset("open-llm-leaderboard/contents")
ds["train"] = ds["train"].select([0])
print (ds["train"][0])
# ds.push_to_hub("TheFinAI/greek-contents")
