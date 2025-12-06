import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
import numpy as np
# from  scipy-learn import sklearn

class FantasyFootballPredictor:

    def __init__(self):
        self.min_mins = 90
        self.chance_to_play = 50
        self.CACHE_DIR = "cache_history"
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR, exist_ok=True)


    def main(self):
        ## refill cache every week

        data = self.get_data()
        players = pd.DataFrame(data["elements"])
        teams = pd.DataFrame(data["teams"])
        events = pd.DataFrame(data["events"])
        self.check_data_current(events)
        active_players = self.get_active_players(players)
        history = self.thread_function_for_player_data(active_players)
        history["expected_goals"] = history["expected_goals"].astype(float)
        history["expected_assists"] = history["expected_assists"].astype(float)
        recent = self.player_form(history)
        team_strength = self.opponent_difficulty(events)

        df = players.merge(recent, left_on="id", right_on="id", how="left")
        df = df.merge(team_strength, left_on="team", right_on="team", how="left")
        df = self.prediction_score(df)

        x=1

    def get_data(self):

        data = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        return data

    def check_data_current(self, events):
        ## before deadline, next will be the upcoming gw
        current_gw = events.loc[events["is_current"] == True, "id"].values[0]
        next_gw = events.loc[events["is_next"] == True, "id"].values[0]

        print("Current GW:", current_gw)
        print("Next GW:", next_gw)
        dates = {}
        dates['current'] = current_gw
        dates['next'] = next_gw
        for gw in ['current', 'next']:
            row = events.loc[events["id"] == dates[gw]]
            start = pd.to_datetime(row["deadline_time"].values[0])
            print(f'GW {gw} start: {start}')



    def get_active_players(self, players):
        # Filter to only players who reasonably play next GW
        active_players = players[
            (players["minutes"] > self.min_mins) &  # Played at least one full match this season
            (players["chance_of_playing_next_round"].fillna(100) > self.chance_to_play)
            ]["id"].tolist()
        print('Total number of active players: ', len(active_players))
        return active_players


    def get_player_history_df(self, player_id):

        cache_file = f"{self.CACHE_DIR}/{player_id}.json" ## refill cache every week
        if os.path.exists(cache_file):
            print(f'Cache for {player_id}')
            return pd.read_json(cache_file)

        url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
        try:
            r = requests.get(url).json()["history"]
            df = pd.DataFrame(r)
            df["element"] = player_id
            df.to_json(cache_file, orient="records")
            return df
        except:
            return None

    def thread_function_for_player_data(self, active_players):

        history_frames = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(self.get_player_history_df, pid): pid for pid in active_players}
            for future in as_completed(futures):
                df = future.result()
                if df is not None:
                    history_frames.append(df)
                    print(len(history_frames))
        print('Threading complete')
        history = pd.concat(history_frames, ignore_index=True)
        return history

    def player_form(self, history):
        recent = history.groupby("element").tail(4).groupby("element").agg({
            "goals_scored": "mean",
            "assists": "mean",
            "expected_goals": "mean",
            "expected_assists": "mean",
            "minutes": "mean",
            "total_points": "mean"
        }).reset_index()
        recent.columns = ["id"] + [f"form_{c}" for c in recent.columns if c != "element"]
        return recent

    def opponent_difficulty(self, events):
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
        return team_strength

    def prediction_score(self, df):

        df["score"] = (
                0.5 * df["form_total_points"].fillna(0) +
                0.3 * (df["form_expected_goals"] + df["form_expected_assists"]).fillna(0) +
                0.2 * df["form_minutes"].fillna(0) / 90 -
                0.1 * df["difficulty"].fillna(3)  # lower difficulty = better
        )
        return df


if __name__ == '__main__':
    FF = FantasyFootballPredictor()
    FF.main()

