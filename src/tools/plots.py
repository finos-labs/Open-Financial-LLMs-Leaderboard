import pandas as pd
import numpy as np
import plotly.express as px
from plotly.graph_objs import Figure

from src.leaderboard.filter_models import FLAGGED_MODELS
from src.display.utils import human_baseline_row as HUMAN_BASELINE, AutoEvalColumn, Tasks, Task, BENCHMARK_COLS
from src.leaderboard.read_evals import EvalResult



def create_scores_df(raw_data: list[EvalResult]) -> pd.DataFrame:
    """
    Generates a DataFrame containing the maximum scores until each date.

    :param results_df: A DataFrame containing result information including metric scores and dates.
    :return: A new DataFrame containing the maximum scores until each date for every metric.
    """
    # Step 1: Ensure 'date' is in datetime format and sort the DataFrame by it
    results_df = pd.DataFrame(raw_data)
    #results_df["date"] = pd.to_datetime(results_df["date"], format="mixed", utc=True)
    results_df.sort_values(by="date", inplace=True)

    # Step 2: Initialize the scores dictionary
    scores = {k: [] for k in BENCHMARK_COLS + [AutoEvalColumn.average.name]}

    # Step 3: Iterate over the rows of the DataFrame and update the scores dictionary
    for task in [t.value for t in Tasks] + [Task("Average", "avg", AutoEvalColumn.average.name)]:
        current_max = 0
        last_date = ""
        column = task.col_name
        for _, row in results_df.iterrows():
            current_model = row["full_model"]
            if current_model in FLAGGED_MODELS:
                continue

            current_date = row["date"]
            if task.benchmark == "Average":
                current_score = np.mean(list(row["results"].values()))
            else:
                current_score = row["results"][task.benchmark]

            if current_score > current_max:
                if current_date == last_date and len(scores[column]) > 0:
                    scores[column][-1] = {"model": current_model, "date": current_date, "score": current_score}
                else:
                    scores[column].append({"model": current_model, "date": current_date, "score": current_score})
                current_max = current_score
                last_date = current_date

    # Step 4: Return all dictionaries as DataFrames
    return {k: pd.DataFrame(v) for k, v in scores.items()}


def create_plot_df(scores_df: dict[str: pd.DataFrame]) -> pd.DataFrame:
    """
    Transforms the scores DataFrame into a new format suitable for plotting.

    :param scores_df: A DataFrame containing metric scores and dates.
    :return: A new DataFrame reshaped for plotting purposes.
    """
    # Initialize the list to store DataFrames
    dfs = []

    # Iterate over the cols and create a new DataFrame for each column
    for col in BENCHMARK_COLS + [AutoEvalColumn.average.name]:
        d = scores_df[col].reset_index(drop=True)
        d["task"] = col
        dfs.append(d)

    # Concatenate all the created DataFrames
    concat_df = pd.concat(dfs, ignore_index=True)

    # Sort values by 'date'
    concat_df.sort_values(by="date", inplace=True)
    concat_df.reset_index(drop=True, inplace=True)
    return concat_df


def create_metric_plot_obj(
    df: pd.DataFrame, metrics: list[str], title: str
) -> Figure:
    """
    Create a Plotly figure object with lines representing different metrics
    and horizontal dotted lines representing human baselines.

    :param df: The DataFrame containing the metric values, names, and dates.
    :param metrics: A list of strings representing the names of the metrics
                    to be included in the plot.
    :param title: A string representing the title of the plot.
    :return: A Plotly figure object with lines representing metrics and
             horizontal dotted lines representing human baselines.
    """

    # Filter the DataFrame based on the specified metrics
    df = df[df["task"].isin(metrics)]

    # Filter the human baselines based on the specified metrics
    filtered_human_baselines = {k: v for k, v in HUMAN_BASELINE.items() if k in metrics}

    # Create a line figure using plotly express with specified markers and custom data
    fig = px.line(
        df,
        x="date",
        y="score",
        color="task",
        markers=True,
        custom_data=["task", "score", "model"],
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
