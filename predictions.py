#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 22:13:52 2026

@author: xavierlee
"""

#scraping epl table from espn
from datetime import datetime, timedelta
import os
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from scipy.stats import poisson
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

url = "https://www.espn.com/soccer/table"
table = pd.read_html(url)
# print(len(table))
# print(table[0])
# print(table[1])

teams_raw = table[0]
standings = table[1]

teams = pd.DataFrame()

teams["position"] = (teams_raw.iloc[:,0].str.extract(r"^(\d+)").astype(int))
teams["team"] = teams_raw.iloc[:,0].str.replace(r"^(\d+)", "", regex = True).str.replace(r"^[A-Z]{3}", "", regex = True).str.strip()

standings = standings.apply(lambda c: c.astype(int))


table = pd.concat([teams, standings], axis = 1)
print(table)

