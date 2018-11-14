import pandas as pd
from flood_data.project_db_scripts.get_server_data import data_dir
df = pd.read_csv('{}/norfolk_flooded_roads_data/STORM_data_flooded_streets_2010-2016_orig.csv'.format(data_dir))
df['location'] = df['location'].str.strip()
df_dups = pd.read_csv('duplicates.csv')

dup = []
for i in range(len(df.location)):
    loc_orig = df.location[i]
    for j in range(len(df_dups.a)):
        loc_dup = df_dups.a[j]
        if loc_orig == loc_dup:
            df.location[i] = df_dups.b[j]
            dup.append(df_dups.a[j])
            print df_dups.a[j]
pd.Series(dup).to_csv('duplicates_removed.csv')
df.to_csv('{}/norfolk_flooded_roads_data/STORM_data_flooded_streets_2010-2016_no_duplicates.csv'.format(data_dir))
