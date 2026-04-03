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
print(fixtures[["utcDate", "homeTeam.name", "awayTeam.name", "score.fullTime.home", "score.fullTime.away"]].head(10))



