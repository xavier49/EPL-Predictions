#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 22:13:52 2026

@author: xavierlee
"""


from datetime import datetime, timedelta
import os
import numpy as np
import requests
import pandas as pd
import requests
from io import StringIO
from dotenv import load_dotenv
from scipy.stats import poisson
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

#scraping epl table from espn
url = "https://www.espn.com/soccer/table"
table = pd.read_html(url)

teams_raw = table[0]
standings = table[1]

#removing abbreviated team names and seperating position and team
teams = pd.DataFrame()
teams["position"] = (teams_raw.iloc[:,0].str.extract(r"^(\d+)").astype(int))
teams["team"] = teams_raw.iloc[:,0].str.replace(r"^(\d+)", "", regex = True).str.replace(r"^[A-Z]{3}", "", regex = True).str.strip()

standings.columns = ["gp", "w", "d", "l", "gf", "ga", "gd", "pts"]
standings = standings.apply(lambda c: c.astype(int))
epl_table = pd.concat([teams, standings], axis = 1)



#scraping fixture list from football-data.org
load_dotenv()
api_key = os.getenv("FOOTBALL_API_KEY")
headers = {"X-Auth-Token": api_key}
url = "https://api.football-data.org/v4/competitions/PL/matches"
response = requests.get(url, headers=headers)
matches = response.json()
fixtures = pd.json_normalize(matches["matches"])


#print(matches.keys())

matches_played = matches["resultSet"]["played"]
#print(matches_played)

today = datetime.utcnow().date()
season_end = today + timedelta(days=365)
#print(fixtures.columns)
fixtures_clean = pd.DataFrame(fixtures[fixtures["status"] == "TIMED"][["utcDate", "status", "homeTeam.name", "awayTeam.name"]].reset_index(drop=True))
fixtures_clean.columns = ["Date", "status", "homeTeam", "awayTeam"]


#obtaining previous results
params = {"season":2025, 
          "status": "FINISHED"}
response = requests.get(url, headers = headers, params = params)
past_matches25 = response.json()
past_fixtures25 = pd.json_normalize(past_matches25["matches"])
past_fixtures_clean25 = past_fixtures25[["utcDate", "matchday", "status", "homeTeam.name", "awayTeam.name", "score.fullTime.home", "score.fullTime.away", "score.winner"]]
past_fixtures_clean25.columns = ["utcDate", "matchday", "status", "homeTeam", "awayTeam", "homeGoals", "awayGoals", "result"]


params = {"season":2024, 
          "status": "FINISHED"}
response = requests.get(url, headers = headers, params = params)
past_matches24 = response.json()
past_fixtures24 = pd.json_normalize(past_matches24["matches"])
past_fixtures_clean24 = past_fixtures24[["utcDate", "matchday", "status", "homeTeam.name", "awayTeam.name", "score.fullTime.home", "score.fullTime.away", "score.winner"]]
past_fixtures_clean24.columns = ["utcDate", "matchday", "status", "homeTeam", "awayTeam", "homeGoals", "awayGoals", "result"]

past_fixtures_clean = pd.concat([past_fixtures_clean25, past_fixtures_clean24], axis = 0).reset_index(drop = True)

#applying weights to past fixtures based on recency
df_played = past_fixtures_clean.sort_values(by = "utcDate")
df_played["weight"] = np.linspace(1,2,len(df_played))




teams = pd.unique(df_played[["homeTeam", "awayTeam"]].values.ravel("K"))



#vectorizing this operation
#weighted averages for goals scored and against - recent games are more impactful
home = df_played.groupby("homeTeam").apply(lambda x: pd.Series({
    "goals_scored": (x["homeGoals"]*x["weight"]).sum() / x["weight"].sum(),
    "goals_against": (x["awayGoals"]*x["weight"]).sum() / x["weight"].sum()
    }), include_groups = False)
away = df_played.groupby("awayTeam").apply(lambda x: pd.Series({
    "goals_scored": (x["awayGoals"]*x["weight"]).sum() / x["weight"].sum(),
    "goals_against": (x["homeGoals"]*x["weight"]).sum() / x["weight"].sum()
    }), include_groups = False)

#team_stats = pd.DataFrame((home + away) / 2)
team_stats = pd.concat([home, away], axis = 1)
team_stats.columns = ["home_goals_scored", "home_goals_against", "away_goals_scored", "away_goals_against"]
league_avg_score = (df_played["homeGoals"].mean() + df_played["awayGoals"].mean())/2
team_stats["home_attack"] = team_stats["home_goals_scored"]/league_avg_score
team_stats["home_defense"] = team_stats["home_goals_against"] / league_avg_score
team_stats["away_attack"] = team_stats["away_goals_scored"]/league_avg_score
team_stats["away_defense"] = team_stats["away_goals_against"] / league_avg_score


def match_probs(home, away):
    xg_home = league_avg_score*team_stats.loc[home]["home_attack"]*team_stats.loc[away]["away_defense"]
    xg_away = league_avg_score*team_stats.loc[away]["away_attack"]*team_stats.loc[home]["home_defense"]
    
    max_goals = 6
    p_home = poisson.pmf(range(max_goals+1), xg_home)
    p_away = poisson.pmf(range(max_goals+1), xg_away)
    
    prob_matrix = np.outer(p_home, p_away)
    p_home_win = np.tril(prob_matrix, -1).sum()
    p_draw = np.diag(prob_matrix).sum()
    p_away_win = np.triu(prob_matrix, 1).sum()
    
    return p_home_win, p_draw, p_away_win

def get_probs(row):
    p_home_win, p_draw, p_away_win = match_probs(row["homeTeam"], row["awayTeam"])
    return pd.Series({
        "p_home_win": p_home_win,
        "p_draw": p_draw,
        "p_away_win": p_away_win
        })
fixture_probs = fixtures_clean.copy()
fixture_probs[["p_home_win", "p_draw", "p_away_win"]] = fixtures_clean.apply(get_probs, axis=1)
    









