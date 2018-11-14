from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from db_scripts.main_db_script import data_dir, db_filename
from hr_db_scripts.main_db_script import get_table_for_variable_code, get_db_table_as_df
import pandas as pd
import matplotlib.pyplot as plt

df = get_db_table_as_df('for_model_avgs', dbfilename=db_filename)
print df.shape
df = df[df.rd>0.01]
print df.shape
out_col = 'num_flooded'
in_cols = [a for a in df.columns if a not in ['event_date', 'event_name']]
reg = RandomForestRegressor()
reg.fit(df[in_cols], df[out_col])
preds = reg.predict(df[in_cols])
maxval = df[out_col].max()
fig, ax = plt.subplots(1)
ax.scatter(df.num_flooded, preds)
ax.set_aspect('equal', adjustable='box-forced')
ax.set_xlim((0, maxval*1.05))
ax.set_ylim((0, maxval*1.05))
plt.show()

