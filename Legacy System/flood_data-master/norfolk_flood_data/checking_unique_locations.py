# coding: utf-8
import pandas as pd
from flood_data.project_db_scripts.get_server_data import data_dir

def clean_lists(l, first):
    combined = [a[0] + "&" + a[1] for a in l]
    combined_clean = [a.replace("'", "") for a in combined]
    if first:
        combined_clean = [a.replace("&", " & ") for a in combined_clean]
    else:
        combined_clean = [a.replace("&", " &") for a in combined_clean]
    combined_clean = [a.strip() for a in combined_clean]
    return combined_clean


df1 = pd.read_csv('{}/norfolk_flooded_roads_data/STORM_data_flooded_streets_2010-2016_orig.csv'.format(data_dir))
df1['location'] = df1['location'].str.strip()
locations = df1.loc[:,'location']
locations = pd.Series(locations.unique())
loc_split = locations.str.split('&')

for i in range(len(loc_split)):
    loc_split[i] = [a.strip() for a in loc_split[i]]
loc_split_strs = loc_split.astype(str)

sorted_loc_split = loc_split
for i in range(len(sorted_loc_split)):
    sorted_loc_split[i].sort()
sorted_loc_strs = sorted_loc_split.astype(str)

duplicates = sorted_loc_strs[sorted_loc_strs.duplicated()]
lists = [d.replace('[','') for d in duplicates]
lists = [d.replace(']','') for d in lists]
a_list = [(d.split(',')[1], d.split(',')[0]) for d in lists]
b_list = [(d.split(',')[0], d.split(',')[1]) for d in lists]

a_list = clean_lists(a_list, 1)
b_list = clean_lists(b_list, 0)
dups = pd.DataFrame({'a': a_list, 'b': b_list})
dups.to_csv('{}/norfolk_flooded_roads_data/duplicates.csv'.format(data_dir))
