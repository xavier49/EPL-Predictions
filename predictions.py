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