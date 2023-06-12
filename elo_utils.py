from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd
from datasets import load_dataset

from content import PLOT_1_TITLE, PLOT_2_TITLE, PLOT_3_TITLE, PLOT_4_TITLE
from utils import make_clickable_model
from visualizations import (get_bootstrap_result, switch_model_a_b,
                            visualize_battle_count, visualize_bootstrap_scores,
                            visualize_pairwise_win_fraction,
                            visualize_rating_count)


@dataclass
class EloEvalResult:
    model: str
    gpt_4_all: int
    human_all: int
    human_instruct: int
    human_code_instruct: int
    tie_allowed: bool

    def to_dict(self):
        base_model = f"{self.model}"
        data_dict = {}
        data_dict["Model"] = make_clickable_model(base_model)
        data_dict["GPT-4 (all)"] = self.gpt_4_all
        data_dict["Human (all)"] = self.human_all
        data_dict["Human (instruct)"] = self.human_instruct
        data_dict["Human (code-instruct)"] = self.human_code_instruct

        return data_dict


def create_eval_df(df, tie_allowed):
    responses = []
    for _, row in df.iterrows():
        if row["status"] == "canceled":
            continue

        rating = row["response"]["annotations"]["Preference"]
        if rating == "NaN":
            continue

        scores = row["response"]["responses"]
        if any(s["Preference"] == "" for s in scores):
            continue

        response = {
            "id": row["task_id"],
            "prompt": row["params"]["templateVariables"]["prompt"],
            "model_a": row["params"]["templateVariables"]["modela"],
            "model_b": row["params"]["templateVariables"]["modelb"],
            "response_a": row["params"]["templateVariables"]["response1"],
            "response_b": row["params"]["templateVariables"]["response2"],
            "rating": int(rating),
            "ratings": [np.array([s["Preference"] for s in scores], dtype=np.int32)],
        }

        if tie_allowed:
            response["win"] = "model_a" if response["rating"] < 4 else "model_b" if response["rating"] > 5 else "tie"
        else:
            response["win"] = "model_a" if response["rating"] < 5 else "model_b"

        responses.append(response)

    return pd.DataFrame(responses)


def create_eval_df_for_gpt(df, tie_allowed):
    responses = []
    for _, row in df.iterrows():
        response = {
            "id": row["review_id"],
            "prompt": row["question"],
            "model_a": row["model1"],
            "model_b": row["model2"],
            "response_a": row["answer1"],
            "response_b": row["answer2"],
            "rating": row["score"][0],
        }

        if tie_allowed:
            response["win"] = "model_a" if response["rating"] < 4 else "model_b" if response["rating"] > 5 else "tie"
        else:
            response["win"] = "model_a" if response["rating"] < 5 else "model_b"

        responses.append(response)

    return pd.DataFrame(responses)


# Compute the Elo rating for each model
def compute_elo(df, k=32, scale=400, base=10, initial_rating=1000):
    rating = defaultdict(lambda: initial_rating)

    for _, model_a, model_b, win in df[["model_a", "model_b", "win"]].itertuples():
        ra = rating[model_a]
        rb = rating[model_b]
        ea = 1 / (1 + base ** ((rb - ra) / scale))
        eb = 1 / (1 + base ** ((ra - rb) / scale))
        if win == "model_a":
            sa = 1
        elif win == "model_b":
            sa = 0
        elif win == "tie" or win == "tie (bothbad)":
            sa = 0.5
        else:
            raise Exception(f"unexpected vote {win}")
        rating[model_a] += k * (sa - ea)
        rating[model_b] += k * (1 - sa - eb)

    return rating


def convert_rating_from_float_to_int(df):
    return {model: int(rating) for model, rating in compute_elo(df).items()}


def get_elo_results(df_instruct, df_code_instruct, tie_allowed):
    df_all = pd.concat([df_instruct, df_code_instruct])

    df_gpt_4 = load_dataset(
        "gpt_4_evals/data/", split="train", revision="e007baaf6e505731c08a0bc1a833a1f8f8cb8846"
    ).to_pandas()

    dfs = [df_instruct, df_code_instruct, df_all]
    elo_ratings = [convert_rating_from_float_to_int(create_eval_df(df, tie_allowed=tie_allowed)) for df in dfs]

    gpt_4_elo_ratings = convert_rating_from_float_to_int(create_eval_df_for_gpt(df_gpt_4, tie_allowed=tie_allowed))
    elo_ratings.append(gpt_4_elo_ratings)

    results = [
        EloEvalResult(
            model=model_name,
            gpt_4_all=elo_ratings[3][model_name],
            human_all=elo_ratings[2][model_name],
            human_instruct=elo_ratings[0][model_name],
            human_code_instruct=elo_ratings[1][model_name],
            tie_allowed=tie_allowed,
        )
        for model_name in elo_ratings[0].keys()
    ]

    return results


def get_elo_results_dicts(df_instruct, df_code_instruct, tie_allowed) -> List[Dict]:
    eval_results = get_elo_results(df_instruct, df_code_instruct, tie_allowed)
    return [r.to_dict() for r in eval_results]


def get_elo_plots(df_instruct, df_code_instruct, tie_allowed):
    df_instruct = create_eval_df(df_instruct, tie_allowed=tie_allowed)
    df_code_instruct = create_eval_df(df_code_instruct, tie_allowed=tie_allowed)
    df_all = pd.concat([df_instruct, df_code_instruct])
    game = df_all[["model_a", "model_b", "win"]]

    game_switch = switch_model_a_b(game)
    plot_1 = visualize_pairwise_win_fraction(game_switch, PLOT_1_TITLE)

    plot_2 = visualize_battle_count(game_switch, PLOT_2_TITLE)

    BOOTSTRAP_ROUNDS = 1000
    if "bootstrap_elo_lu" not in globals():
        bootstrap_elo_lu = get_bootstrap_result(game_switch, compute_elo, BOOTSTRAP_ROUNDS)

    plot_3 = visualize_bootstrap_scores(bootstrap_elo_lu, PLOT_3_TITLE)

    plot_4 = visualize_rating_count(game, PLOT_4_TITLE)

    return plot_1, plot_2, plot_3, plot_4
