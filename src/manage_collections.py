import os
import pandas as pd
from pandas import DataFrame
from huggingface_hub import get_collection, add_collection_item, delete_collection_item
from huggingface_hub.utils._errors import HfHubHTTPError

from src.display_models.model_metadata_type import ModelType
from src.display_models.utils import AutoEvalColumn

H4_TOKEN = os.environ.get("H4_TOKEN", None)

path_to_collection = "open-llm-leaderboard/llm-leaderboard-best-models-652d6c7965a4619fb5c27a03"
intervals = {
    "1B": pd.Interval(0, 1.5, closed="right"),
    "3B": pd.Interval(2.5, 3.5, closed="neither"),
    "7B": pd.Interval(6, 8, closed="neither"),
    "13B": pd.Interval(10, 14, closed="neither"),
    "30B":pd.Interval(25, 35, closed="neither"), 
    "65B": pd.Interval(60, 70, closed="neither"),
}

def update_collections(df: DataFrame):
    """This function updates the Open LLM Leaderboard model collection with the latest best models for 
    each size category and type.
    """
    params_column = pd.to_numeric(df[AutoEvalColumn.params.name], errors="coerce")

    cur_best_models = []

    for type in ModelType:
        if type.value.name == "": continue
        for size in intervals:
            # We filter the df to gather the relevant models
            type_emoji = [t[0] for t in type.value.symbol]
            filtered_df = df[df[AutoEvalColumn.model_type_symbol.name].isin(type_emoji)]

            numeric_interval = pd.IntervalIndex([intervals[size]])
            mask = params_column.apply(lambda x: any(numeric_interval.contains(x)))
            filtered_df = filtered_df.loc[mask]

            best_models = list(filtered_df.sort_values(AutoEvalColumn.average.name, ascending=False)[AutoEvalColumn.dummy.name])
            print(type.value.symbol, size, best_models[:10])

            # We add them one by one to the leaderboard
            for model in best_models:
                # We can use collection = get_collection to grab the id of the last item, then place it where we want using update_collection but it's costly...
                # We could also remove exists_ok to update the note to include the date of apparition of the model for ex.
                try:
                    add_collection_item(
                        path_to_collection, 
                        item_id=model, 
                        item_type="model", 
                        exists_ok=True, 
                        note=f"Best {type.to_str(' ')} model of around {size} on the leaderboard today!", 
                        token=H4_TOKEN
                    )
                    cur_best_models.append(model)
                    break
                except HfHubHTTPError:
                    continue

    collection = get_collection(path_to_collection, token=H4_TOKEN)
    for item in collection.items:
        if item.item_id not in cur_best_models:
            delete_collection_item(collection_slug=path_to_collection, item_object_id=item.item_object_id, token=H4_TOKEN)

