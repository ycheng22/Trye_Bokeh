# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 00:33:36 2021

@author: Yunpeng Cheng

@E_mail: ycheng22@hotmail.com

@Github: https://github.com/ycheng22

Reference:
"""
#I will focus on coding in notebook before coding python scripts

import sys
sys.path.insert(0, './scripts')
import pandas as pd
import numpy as np

# Bokeh basics 
from bokeh.io import curdoc, show
from bokeh.models import Tabs, Column, Row

from routes import route_tab


# Load in flights and inspect
flights = pd.read_csv('./data/Hou_flights.csv', index_col=0).dropna()

# Create each of the tabs
tab_route = route_tab(flights)

# Put all the tabs into one application
tabs = Tabs(tabs = [tab_route])
#show(tabs)
# Put the tabs in the current document for display
curdoc().add_root(tabs)

#in the app_demo folder, activate python env, run bokeh serve --show main.py
