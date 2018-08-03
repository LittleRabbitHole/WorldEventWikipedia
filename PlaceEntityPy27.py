#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 22:44:26 2018

@author: Ang
"""

import pandas as pd

data = pd.read_table("/Users/Ang/GoogleDrive/GoogleDrive_Pitt_PhD/UPitt_PhD_O/Research/WorldEvents&Wikipedia/data/results_v1.csv", 
                             sep=',', error_bad_lines = False)  

data.columns.values

data['header'].iloc[0]
