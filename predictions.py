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