import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt

df_raw = pd.read_csv('data/rev_candidate_full.csv')
df_o1 = df_raw.loc[lambda df: df['order'] == 1]
df_o2 = df_raw.loc[lambda df: df['order'] == 2]
df_o3 = df_raw.loc[lambda df: df['order'] == 3]
df_o4 = df_raw.loc[lambda df: df['order'] == 4]

# ref = df_o1['references']
# std_ref = 

# plot = df_o1.plot(kind='bar',yerr=stdsum,colormap='OrRd_r',edgecolor='black',grid=False,figsize=(8,2),ax=ax,position=0.45,error_kw=dict(ecolor='black',elinewidth=0.5),width=0.8)

box_group = df_o1.boxplot(column=['references'], by=['topic'], showfliers=False)
# gp1 = df_o1.groupby(level=['topic'])
# mean = gp1.mean()
# std = gp1.std()

# fig, ax = plt.subplots()

# mean.plot.bar(yerr=std, ax=ax)
plt.show()