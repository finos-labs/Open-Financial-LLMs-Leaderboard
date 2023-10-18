import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure
import pickle
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Any
from src.display_models.model_metadata_flags import FLAGGED_MODELS

# Average ⬆️ human baseline is 0.897 (source: averaging human baselines below)
# ARC human baseline is 0.80 (source: https://lab42.global/arc/)
# HellaSwag human baseline is 0.95 (source: https://deepgram.com/learn/hellaswag-llm-benchmark-guide)
# MMLU human baseline is 0.898 (source: https://openreview.net/forum?id=d7KBjmI3GmQ)
# TruthfulQA human baseline is 0.94(source: https://arxiv.org/pdf/2109.07958.pdf)
# Define the human baselines
HUMAN_BASELINES = {
    "Average ⬆️": 0.897 * 100,
    "ARC": 0.80 * 100,
    "HellaSwag": 0.95 * 100,
    "MMLU": 0.898 * 100,
    "TruthfulQA": 0.94 * 100,
}


def to_datetime(model_info: Tuple[str, Any]) -> datetime:
    """
    Converts the lastModified attribute of the object to datetime.

    :param model_info: A tuple containing the name and object.
                       The object must have a lastModified attribute
                       with a string representing the date and time.
    :return: A datetime object converted from the lastModified attribute of the input object.
    """
    name, obj = model_info
    return datetime.strptime(obj.lastModified, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def join_model_info_with_results(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Integrates model information with the results DataFrame by matching 'Model sha'.
    :param results_df: A DataFrame containing results information including 'Model sha' column.
    :return: A DataFrame with updated 'Results Date' columns, which are synchronized with model information.
    """
    # copy dataframe to avoid modifying the original
    df = results_df.copy(deep=True)

    # Filter out FLAGGED_MODELS to ensure graph is not skewed by mistakes
    df = df[~df["model_name_for_query"].isin(FLAGGED_MODELS.keys())].reset_index(drop=True)

    # load cache from disk
    try:
        with open("model_info_cache.pkl", "rb") as f:
            model_info_cache = pickle.load(f)
    except (EOFError, FileNotFoundError):
        model_info_cache = {}

    # Sort date strings using datetime objects as keys
    sorted_dates = sorted(list(model_info_cache.items()), key=to_datetime, reverse=True)
    df["Results Date"] = datetime.now().replace(tzinfo=timezone.utc)

    # Define the date format string
    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # Iterate over sorted_dates and update the dataframe
    for name, obj in sorted_dates:
        # Convert the lastModified string to a datetime object
        last_modified_datetime = datetime.strptime(obj.lastModified, date_format).replace(tzinfo=timezone.utc)

        # Update the "Results Date" column where "Model sha" equals obj.sha
        df.loc[df["Model sha"] == obj.sha, "Results Date"] = last_modified_datetime
    return df


def create_scores_df(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates a DataFrame containing the maximum scores until each result date.

    :param results_df: A DataFrame containing result information including metric scores and result dates.
    :return: A new DataFrame containing the maximum scores until each result date for every metric.
    """
    # Step 1: Ensure 'Results Date' is in datetime format and sort the DataFrame by it
    results_df["Results Date"] = pd.to_datetime(results_df["Results Date"])
    results_df.sort_values(by="Results Date", inplace=True)

    # Step 2: Initialize the scores dictionary
    scores = {
        "Average ⬆️": [],
        "ARC": [],
        "HellaSwag": [],
        "MMLU": [],
        "TruthfulQA": [],
        "Result Date": [],
        "Model Name": [],
    }

    # Step 3: Iterate over the rows of the DataFrame and update the scores dictionary
    for i, row in results_df.iterrows():
        date = row["Results Date"]
        for column in scores.keys():
            if column == "Result Date":
                if not scores[column] or scores[column][-1] <= date:
                    scores[column].append(date)
                continue
            if column == "Model Name":
                scores[column].append(row["model_name_for_query"])
                continue
            current_max = scores[column][-1] if scores[column] else float("-inf")
            scores[column].append(max(current_max, row[column]))

    # Step 4: Convert the dictionary to a DataFrame
    return pd.DataFrame(scores)


def create_plot_df(scores_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the scores DataFrame into a new format suitable for plotting.

    :param scores_df: A DataFrame containing metric scores and result dates.
    :return: A new DataFrame reshaped for plotting purposes.
    """
    # Sample columns
    cols = ["Average ⬆️", "ARC", "HellaSwag", "MMLU", "TruthfulQA"]

    # Initialize the list to store DataFrames
    dfs = []

    # Iterate over the cols and create a new DataFrame for each column
    for col in cols:
        d = scores_df[[col, "Model Name", "Result Date"]].copy().reset_index(drop=True)
        d["Metric Name"] = col
        d.rename(columns={col: "Metric Value"}, inplace=True)
        dfs.append(d)

    # Concatenate all the created DataFrames
    concat_df = pd.concat(dfs, ignore_index=True)

    # Sort values by 'Result Date'
    concat_df.sort_values(by="Result Date", inplace=True)
    concat_df.reset_index(drop=True, inplace=True)

    # Drop duplicates based on 'Metric Name' and 'Metric Value' and keep the first (earliest) occurrence
    concat_df.drop_duplicates(subset=["Metric Name", "Metric Value"], keep="first", inplace=True)

    concat_df.reset_index(drop=True, inplace=True)
    return concat_df


def create_metric_plot_obj(
    df: pd.DataFrame, metrics: List[str], human_baselines: Dict[str, float], title: str
) -> Figure:
    """
    Create a Plotly figure object with lines representing different metrics
    and horizontal dotted lines representing human baselines.

    :param df: The DataFrame containing the metric values, names, and dates.
    :param metrics: A list of strings representing the names of the metrics
                    to be included in the plot.
    :param human_baselines: A dictionary where keys are metric names
                            and values are human baseline values for the metrics.
    :param title: A string representing the title of the plot.
    :return: A Plotly figure object with lines representing metrics and
             horizontal dotted lines representing human baselines.
    """

    # Filter the DataFrame based on the specified metrics
    df = df[df["Metric Name"].isin(metrics)]

    # Filter the human baselines based on the specified metrics
    filtered_human_baselines = {k: v for k, v in human_baselines.items() if k in metrics}

    # Create a line figure using plotly express with specified markers and custom data
    fig = px.line(
        df,
        x="Result Date",
        y="Metric Value",
        color="Metric Name",
        markers=True,
        custom_data=["Metric Name", "Metric Value", "Model Name"],
        title=title,
    )

    # Update hovertemplate for better hover interaction experience
    fig.update_traces(
        hovertemplate="<br>".join(
            [
                "Model Name: %{customdata[2]}",
                "Metric Name: %{customdata[0]}",
                "Date: %{x}",
                "Metric Value: %{y}",
            ]
        )
    )

    # Update the range of the y-axis
    fig.update_layout(yaxis_range=[0, 100])

    # Create a dictionary to hold the color mapping for each metric
    metric_color_mapping = {}

    # Map each metric name to its color in the figure
    for trace in fig.data:
        metric_color_mapping[trace.name] = trace.line.color

    # Iterate over filtered human baselines and add horizontal lines to the figure
    for metric, value in filtered_human_baselines.items():
        color = metric_color_mapping.get(metric, "blue")  # Retrieve color from mapping; default to blue if not found
        location = "top left" if metric == "HellaSwag" else "bottom left"  # Set annotation position
        # Add horizontal line with matched color and positioned annotation
        fig.add_hline(
            y=value,
            line_dash="dot",
            annotation_text=f"{metric} human baseline",
            annotation_position=location,
            annotation_font_size=10,
            annotation_font_color=color,
            line_color=color,
        )

    return fig


# Example Usage:
# human_baselines dictionary is defined.
# chart = create_metric_plot_obj(scores_df, ["ARC", "HellaSwag", "MMLU", "TruthfulQA"], human_baselines, "Graph Title")