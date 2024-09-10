import json
import os
import pandas as pd
import numpy as np

from src.display.formatting import has_no_nan_values, make_clickable_model
from src.display.utils import AutoEvalColumn, EvalQueueColumn
from src.leaderboard.read_evals import get_raw_eval_results


def get_leaderboard_df(results_path: str, requests_path: str, cols: list, benchmark_cols: list) -> pd.DataFrame:
    """Creates a dataframe from all the individual experiment results"""
    raw_data = get_raw_eval_results(results_path, requests_path)
    all_data_json = [v.to_dict() for v in raw_data]

    df = pd.DataFrame.from_records(all_data_json)

    # Add category average columns with default values
    category_avg_columns = {
        "Average IE ⬆️": "average_IE",
        "Average TA ⬆️": "average_TA",
        "Average QA ⬆️": "average_QA",
        "Average TG ⬆️": "average_TG",
        "Average RM ⬆️": "average_RM",
        "Average FO ⬆️": "average_FO",
        "Average DM ⬆️": "average_DM",
        "Average Spanish ⬆️": "average_Spanish"
    }

    for display_name, internal_name in category_avg_columns.items():
        df[display_name] = df[internal_name]

    df = df.sort_values(by=[AutoEvalColumn.average.name], ascending=False)

    def normalize_column(df: pd.DataFrame, col: str):
        """Normalize a column to a 0-100 range based on its min and max values.
        Non-numeric values will be treated as 0."""
        # Convert non-numeric values to 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        min_val = df[col].min()
        max_val = df[col].max()

        # Avoid division by zero if max == min
        if max_val != min_val:
            df[col] = df[col].apply(lambda x: ((x - min_val) / (max_val - min_val)) * 100)
        else:
            df[col] = 100  # if all values are the same, set them to 100 (since they are all "max")

    def normalize_all_columns(df: pd.DataFrame):
        """Normalize all columns in the DataFrame to a 0-100 range, skipping boolean and string columns."""
        for col in df.columns:
            if pd.api.types.is_bool_dtype(df[col]):
                continue
            elif pd.api.types.is_string_dtype(df[col]):
                continue
            elif pd.api.types.is_numeric_dtype(df[col]):
                normalize_column(df, col)
        return df

    # Example usage
    df = normalize_all_columns(df)

    '''
    print(df.columns)
    # Apply the transformation for MCC values
    mcc_tasks = ["German", "Australian", "LendingClub", "ccf", "ccfraud", "polish", "taiwan", "portoseguro", "travelinsurance"]
    for task in mcc_tasks:
        if task in df.columns:
            df[task] = df.apply(lambda row: (row[task] + 100) / 2.0 if row[task] != "missing" else row[task], axis=1)

    for index, row in df.iterrows():
        if "FinTrade" in row and row["FinTrade"] != "missing":
            df.loc[index, "FinTrade"] = (row["FinTrade"] + 300) / 6
    '''
    # Now, select the columns that were passed to the function
    df = df[cols]

    # Function to round numeric values, including those in string format
    def round_numeric(x):
        try:
            return round(float(x), 1)
        except ValueError:
            return x

    # Apply rounding to all columns except 'T' and 'Model'
    for col in df.columns:
        if col not in ['T', 'Model']:
            df[col] = df[col].apply(round_numeric)

    # Filter out if any of the benchmarks have not been produced
    df = df[has_no_nan_values(df, benchmark_cols)]

    return raw_data, df


def get_evaluation_queue_df(save_path: str, cols: list) -> list[pd.DataFrame]:
    """Creates the different dataframes for the evaluation queues requests"""
    entries = [entry for entry in os.listdir(save_path) if not entry.startswith(".")]
    all_evals = []

    for entry in entries:
        if ".json" in entry:
            file_path = os.path.join(save_path, entry)
            with open(file_path) as fp:
                data = json.load(fp)

            data[EvalQueueColumn.model.name] = make_clickable_model(data["model"])
            data[EvalQueueColumn.revision.name] = data.get("revision", "main")

            all_evals.append(data)
        elif ".md" not in entry:
            # this is a folder
            sub_entries = [e for e in os.listdir(f"{save_path}/{entry}") if not e.startswith(".")]
            for sub_entry in sub_entries:
                file_path = os.path.join(save_path, entry, sub_entry)
                with open(file_path) as fp:
                    data = json.load(fp)

                data[EvalQueueColumn.model.name] = make_clickable_model(data["model"])
                data[EvalQueueColumn.revision.name] = data.get("revision", "main")
                all_evals.append(data)

    pending_list = [e for e in all_evals if e["status"] in ["PENDING", "RERUN"]]
    running_list = [e for e in all_evals if e["status"] == "RUNNING"]
    finished_list = [e for e in all_evals if e["status"].startswith("FINISHED") or e["status"] == "PENDING_NEW_EVAL"]
    df_pending = pd.DataFrame.from_records(pending_list, columns=cols)
    df_running = pd.DataFrame.from_records(running_list, columns=cols)
    df_finished = pd.DataFrame.from_records(finished_list, columns=cols)
    return df_finished[cols], df_running[cols], df_pending[cols]
