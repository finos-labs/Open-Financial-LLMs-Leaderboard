import math

import numpy as np
import pandas as pd
import plotly.express as px


# 1
def compute_pairwise_win_fraction(battles):
    # Times each model wins as Model A
    a_win_ptbl = pd.pivot_table(
        battles[battles["win"] == "model_a"],
        index="model_a",
        columns="model_b",
        aggfunc="size",
        fill_value=0,
    )

    # Table counting times each model wins as Model B
    b_win_ptbl = pd.pivot_table(
        battles[battles["win"] == "model_b"],
        index="model_a",
        columns="model_b",
        aggfunc="size",
        fill_value=0,
    )

    # Table counting number of A-B pairs
    num_battles_ptbl = pd.pivot_table(battles, index="model_a", columns="model_b", aggfunc="size", fill_value=0)

    # Computing the proportion of wins for each model as A and as B
    # against all other models
    row_beats_col_freq = (a_win_ptbl + b_win_ptbl.T) / (num_battles_ptbl + num_battles_ptbl.T)

    # Arrange ordering according to proprition of wins
    prop_wins = row_beats_col_freq.mean(axis=1).sort_values(ascending=False)
    model_names = list(prop_wins.keys())
    row_beats_col = row_beats_col_freq.loc[model_names, model_names]
    return row_beats_col


def visualize_pairwise_win_fraction(battles, title):
    row_beats_col = compute_pairwise_win_fraction(battles)
    fig = px.imshow(row_beats_col, color_continuous_scale="RdBu", text_auto=".2f", title=title)
    fig.update_layout(
        xaxis_title="Model B",
        yaxis_title="Model A",
        xaxis_side="top",
        title_y=0.07,
        title_x=0.5,
    )
    fig.update_traces(hovertemplate="Model A: %{y}<br>Model B: %{x}<br>Fraction of A Wins: %{z}<extra></extra>")
    return fig


# 2
def switch_model_a_b(df):
    df_switch = df.copy()
    # switch with probability 0.5
    for i, row in df.iterrows():
        if np.random.rand() < 0.5:
            df_switch.at[i, "model_a"] = row["model_b"]
            df_switch.at[i, "model_b"] = row["model_a"]
            if row["win"] == "model_a":
                df_switch.at[i, "win"] = "model_b"
            elif row["win"] == "model_b":
                df_switch.at[i, "win"] = "model_a"
    return df_switch


def visualize_battle_count(battles, title):
    ptbl = pd.pivot_table(battles, index="model_a", columns="model_b", aggfunc="size", fill_value=0)
    battle_counts = ptbl + ptbl.T
    ordering = battle_counts.sum().sort_values(ascending=False).index
    fig = px.imshow(battle_counts.loc[ordering, ordering], title=title, text_auto=True, width=600)
    fig.update_layout(
        xaxis_title="Model B",
        yaxis_title="Model A",
        xaxis_side="top",
        title_y=0.07,
        title_x=0.5,
    )
    fig.update_traces(hovertemplate="Model A: %{y}<br>Model B: %{x}<br>Count: %{z}<extra></extra>")
    return fig


# 3
def get_bootstrap_result(battles, func_compute_elo, num_round):
    rows = [func_compute_elo(battles.sample(frac=1.0, replace=True)) for _ in range(num_round)]
    df = pd.DataFrame(rows)
    return df[df.median().sort_values(ascending=False).index]


def visualize_bootstrap_scores(df, title):
    bars = (
        pd.DataFrame(
            dict(
                lower=df.quantile(0.025),
                rating=df.quantile(0.5),
                upper=df.quantile(0.975),
            )
        )
        .reset_index(names="model")
        .sort_values("rating", ascending=False)
    )
    bars["error_y"] = bars["upper"] - bars["rating"]
    bars["error_y_minus"] = bars["rating"] - bars["lower"]
    bars["rating_rounded"] = np.round(bars["rating"], 2)
    fig = px.scatter(
        bars,
        x="model",
        y="rating",
        error_y="error_y",
        error_y_minus="error_y_minus",
        text="rating_rounded",
        title=title,
    )
    fig.update_layout(xaxis_title="Model", yaxis_title="Rating")
    return fig


# 4
def visualize_rating_count(df, title):
    df_all_value_counts = pd.concat([df["model_a"], df["model_b"]]).value_counts()
    fig = px.bar(df_all_value_counts, title=title, text_auto=True)

    min_y = df_all_value_counts.min()
    max_y = df_all_value_counts.max()

    y_end = math.ceil(min_y / 100) * 100
    y_begin = math.floor(max_y / 100) * 100

    fig.update_layout(xaxis_title="model", yaxis_title="Rating Count", showlegend=False)
    fig.update_yaxes(range=[y_begin, y_end])
    # save the plot for the blog:
    fig.write_html("model_counts.html", full_html=False, include_plotlyjs="cdn")
    return fig
