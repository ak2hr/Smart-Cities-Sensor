# coding: utf-8
import pandas as pd
import matplotlib.pyplot as plt
from flood_data.project_db_scripts.get_server_data import data_dir, fig_dir
df = pd.read_csv('{}norfolk_flooded_roads_data/STORM_data_flooded_streets_2010-2016_no_duplicates_clean.csv'.format(data_dir))
dates = pd.to_datetime(df['_date'])
df_dates = pd.DataFrame({'dates':dates.unique(), 'count':range(len(dates.unique()))})
df_dates.set_index('dates', inplace=1, drop=1)
df_dates['count'] = df_dates['count'] +1
ax = df_dates.plot()
# ax.fill_between(df_dates.index, df_dates['count'])
ax.set_ylabel('Cummulative days with\n floods reported', fontsize=16)
ax.legend_.remove()
ax.set_xlabel('Date', fontsize=16)
ax.tick_params(axis='both', which='major', labelsize=16)
plt.savefig('{}cummulative_flooded_days'.format(fig_dir))
plt.show()
