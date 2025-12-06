import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
import numpy as np
# from sklearn.ensemble import RandomForestRegressor  # optional later if you add ML


class FantasyFootballPredictor:

    def __init__(self):
        self.min_mins = 90
        self.chance_to_play = 50
        self.CACHE_DIR = "cache_history"
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR, exist_ok=True)

    def main(self, top_n: int = 30):
        """
        Main entry point:
        - Fetch base data
        - Filter active players
        - Get history (threaded + cached)
        - Compute recent form
        - Compute opponent difficulty for next GW
        - Build prediction score
        - Print top N players
        """

        data = self.get_data()
        players = pd.DataFrame(data["elements"])
        teams = pd.DataFrame(data["teams"])
        events = pd.DataFrame(data["events"])

        self.check_data_current(events)

        active_players = self.get_active_players(players)
        history = self.thread_function_for_player_data(active_players)

        # Ensure expected stats exist
        for col in ["expected_goals", "expected_assists"]:
            if col not in history.columns:
                history[col] = 0.0

        # Force numeric types where needed
        history["expected_goals"] = pd.to_numeric(history["expected_goals"], errors="coerce").fillna(0.0)
        history["expected_assists"] = pd.to_numeric(history["expected_assists"], errors="coerce").fillna(0.0)

        recent = self.player_form(history)
        team_strength = self.opponent_difficulty(events)

        # Merge players with recent form & fixture difficulty
        df = players.merge(recent, on="id", how="left")
        df = df.merge(team_strength, on="team", how="left")

        # Add team names for readability
        team_lookup = teams.set_index("id")["name"]
        df["team_name"] = df["team"].map(team_lookup)

        df = self.prediction_score(df)

        # Sort and show results
        cols_to_show = [
            "second_name", "first_name", "team_name", "now_cost",
            "score", "form_total_points", "form_expected_goals",
            "form_expected_assists", "form_minutes", "difficulty",
            "points_per_game", "form"
        ]

        available_cols = [c for c in cols_to_show if c in df.columns]
        top = df.sort_values("score", ascending=False)[available_cols].head(top_n)

        print("\nTop predicted players for next GW:")
        print(top.to_string(index=False))

    # ---------------------------
    # Data fetching & checks
    # ---------------------------

    def get_data(self):
        data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        return data

    def check_data_current(self, events: pd.DataFrame):
        """
        Print current + next GW and their deadlines.
        Useful sanity check that you’re using up-to-date data.
        """
        current_gw = events.loc[events["is_current"] == True, "id"].values[0]
        next_gw = events.loc[events["is_next"] == True, "id"].values[0]

        print("Current GW:", current_gw)
        print("Next GW:", next_gw)
        dates = {"current": current_gw, "next": next_gw}
        for gw in ["current", "next"]:
            row = events.loc[events["id"] == dates[gw]]
            start = pd.to_datetime(row["deadline_time"].values[0])
            print(f"GW {gw} deadline: {start}")

    # ---------------------------
    # Player selection & history
    # ---------------------------

    def get_active_players(self, players: pd.DataFrame):
        """
        Filter to only players likely to play next GW.
        """
        active_players = players[
            (players["minutes"] > self.min_mins) &  # Played at least one full match this season
            (players["chance_of_playing_next_round"].fillna(100) > self.chance_to_play)
        ]["id"].tolist()

        print('Total number of active players: ', len(active_players))
        return active_players

    def get_player_history_df(self, player_id):
        """
        Load player history from cache if available, otherwise fetch from API and cache it.
        """
        cache_file = f"{self.CACHE_DIR}/{player_id}.json"
        if os.path.exists(cache_file):
            # print(f'Cache for {player_id}')
            return pd.read_json(cache_file)

        url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
        try:
            r = requests.get(url).json()["history"]
            df = pd.DataFrame(r)
            df["element"] = player_id
            df.to_json(cache_file, orient="records")
            return df
        except Exception as e:
            print(f"Error fetching history for player {player_id}: {e}")
            return None

    def thread_function_for_player_data(self, active_players):
        """
        Use a ThreadPoolExecutor to fetch histories in parallel.
        """
        history_frames = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(self.get_player_history_df, pid): pid for pid in active_players}
            for i, future in enumerate(as_completed(futures), start=1):
                df = future.result()
                if df is not None:
                    history_frames.append(df)
                if i % 20 == 0:
                    print(f"Fetched histories for {i} players...")

        print('Threading complete; total history frames:', len(history_frames))
        history = pd.concat(history_frames, ignore_index=True)
        return history

    # ---------------------------
    # Feature engineering
    # ---------------------------

    def player_form(self, history: pd.DataFrame):
        """
        Compute recent form for each player over their last 4 matches.
        """
        # Make sure we’re taking the last 4 chronologically
        history_sorted = history.sort_values(["element", "round"])

        recent = history_sorted.groupby("element").tail(4).groupby("element").agg({
            "goals_scored": "mean",
            "assists": "mean",
            "expected_goals": "mean",
            "expected_assists": "mean",
            "minutes": "mean",
            "total_points": "mean"
        }).reset_index()

        # Rename columns: element -> id, others -> form_<stat>
        recent.columns = ["element"] + [c for c in recent.columns if c != "element"]
        recent.rename(columns={"element": "id"}, inplace=True)

        # Prefix form_ for clarity
        rename_map = {
            "goals_scored": "form_goals_scored",
            "assists": "form_assists",
            "expected_goals": "form_expected_goals",
            "expected_assists": "form_expected_assists",
            "minutes": "form_minutes",
            "total_points": "form_total_points",
        }
        recent = recent.rename(columns=rename_map)

        return recent

    def opponent_difficulty(self, events: pd.DataFrame):
        """
        For the next GW, map each team to a single difficulty value.
        If a team has multiple fixtures (double GW), use the average difficulty.
        """
        fixtures = requests.get("https://fantasy.premierleague.com/api/fixtures/").json()
        fixtures = pd.DataFrame(fixtures)

        next_gw = events[events["is_next"] == True].iloc[0]["id"]

        next_fixtures = fixtures[fixtures["event"] == next_gw][[
            "team_h", "team_a", "team_h_difficulty", "team_a_difficulty"
        ]]

        team_strength = pd.concat([
            next_fixtures[["team_h", "team_h_difficulty"]].rename(
                columns={"team_h": "team", "team_h_difficulty": "difficulty"}),
            next_fixtures[["team_a", "team_a_difficulty"]].rename(
                columns={"team_a": "team", "team_a_difficulty": "difficulty"})
        ])

        # If a team plays more than once, average the difficulties
        team_strength = team_strength.groupby("team", as_index=False)["difficulty"].mean()

        return team_strength

    # ---------------------------
    # Scoring model
    # ---------------------------

    def prediction_score(self, df: pd.DataFrame):
        """
        Heuristic scoring model:
        - form_total_points (recent FPL returns)
        - xG + xA (recent underlying attacking stats)
        - recent minutes (availability / nailedness)
        - fixture difficulty (easier is better)
        - optional static form / points_per_game from bootstrap
        """

        # Safeguard for missing columns
        for col in [
            "form_total_points",
            "form_expected_goals",
            "form_expected_assists",
            "form_minutes",
            "difficulty",
            "points_per_game",
            "form",
        ]:
            if col not in df.columns:
                df[col] = np.nan

        df["form_total_points"] = df["form_total_points"].fillna(0)
        df["form_expected_goals"] = df["form_expected_goals"].fillna(0)
        df["form_expected_assists"] = df["form_expected_assists"].fillna(0)
        df["form_minutes"] = df["form_minutes"].fillna(0)
        df["difficulty"] = df["difficulty"].fillna(3)  # neutral difficulty
        df["points_per_game"] = pd.to_numeric(df["points_per_game"], errors="coerce").fillna(0)
        df["form"] = pd.to_numeric(df["form"], errors="coerce").fillna(0)

        # Normalize some features to get them roughly on similar scales
        def safe_norm(col):
            c = df[col]
            if c.max() == c.min():
                return 0 * c
            return (c - c.min()) / (c.max() - c.min())

        norm_minutes = safe_norm("form_minutes")
        norm_ppg = safe_norm("points_per_game")
        norm_form = safe_norm("form")

        # Heuristic weights – tweak as you like
        df["score"] = (
            0.40 * df["form_total_points"] +                                   # recent FPL output
            0.30 * (df["form_expected_goals"] + df["form_expected_assists"]) + # recent xG+xA
            0.15 * norm_minutes +                                              # nailedness
            0.10 * norm_ppg +                                                  # season-long consistency
            0.05 * norm_form -                                                 # FPL's built-in form metric
            0.10 * df["difficulty"]                                            # penalty for harder fixture
        )

        return df


if __name__ == '__main__':
    FF = FantasyFootballPredictor()
    FF.main(top_n=30)
