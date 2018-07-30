import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt

data_set = pd.read_csv("process_analysis.csv",squeeze=True)

# data_set[['IP edits']] = data_set[['IP edits']].apply(pd.to_numeric)

data_set = data_set.assign(P_bot_edit=lambda x: x['Bot edits'] / x['Total edits'],
                           P_revert_edit=lambda x: x['Reverted edits'] / x['Total edits'],
                           P_IP_edit=lambda x: x['IP edits'] / x['Total edits'],
                           P_top_edit=lambda x: x['Edits made by the top 10% of editors'] / x['Total edits'],
                           P_minor_edit=lambda x: x['Minor edits'] / x['Total edits'])

Morpheme = {'en': 'Words', 'es': 'Words', 'cn': "Characters"}

def define_morpheme(row):
    return row[Morpheme[row['language']]]

data_set['morpheme'] = data_set.apply(define_morpheme, axis=1)

data_set = data_set.assign(R_reference=lambda x: x['References'] / x['morpheme'],
                           R_unique_reference=lambda x: x['Unique references'] / x['morpheme'])

en_set = data_set[data_set.language.isin(['en'])]
es_set = data_set[data_set.language.isin(['es'])]
cn_set = data_set[data_set.language.isin(['cn'])]

col_name_T = ['Total edits']
col_name_E = ['Average edits per user']
col_name_R = ['R_reference', 'R_unique_reference']
col_name_L = ['Links from this page', 'Links to this page', 'External links']
col_name_P = ['P_bot_edit', 'P_revert_edit', 'P_IP_edit', 'P_top_edit', 'P_minor_edit']

print(data_set.dtypes)

# box_en = en_set.boxplot(column=col_name)
# box_es = es_set.boxplot(column=col_name)
# box_cn = cn_set.boxplot(column=col_name)

# box_group_TL = data_set.boxplot(column=col_name_T, by=['language'], showfliers=True)
# box_group_TC = data_set.boxplot(column=col_name_T, by=['category'], rot=45, showfliers=True)
# box_group_EL = data_set.boxplot(column=col_name_E, by=['language'], showfliers=True)
# box_group_EC = data_set.boxplot(column=col_name_E, by=['category'], rot=45, showfliers=True)
# box_group_RL = data_set.boxplot(column=col_name_R, by=['language'], showfliers=False)
# box_group_RC = data_set.boxplot(column=col_name_R, by=['category'], rot=60, showfliers=False)
# box_group_LL = data_set.boxplot(column=col_name_L, by=['language'], showfliers=True)
# box_group_LC = data_set.boxplot(column=col_name_L, by=['category'], rot=45, showfliers=True)
# box_group_PL = data_set.boxplot(column=col_name_P, by=['language'], showfliers=True)
# box_group_PC = data_set.boxplot(column=col_name_P, by=['category'], rot=45, showfliers=True)

box_group_RC_en = en_set.boxplot(column=col_name_R, by=['category'], rot=60, showfliers=False)
box_group_RC_es = es_set.boxplot(column=col_name_R, by=['category'], rot=60, showfliers=False)
box_group_RC_cn = cn_set.boxplot(column=col_name_R, by=['category'], rot=60, showfliers=False)

plt.show()
