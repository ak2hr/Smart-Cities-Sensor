import os
import pandas as pd
from main_db_script import data_dir
directory = os.path.dirname(__file__)
intersection_name = 'E VIRGINIA BEACH BOULEVARD & TIDEWATER DRIVE'
flood_df = pd.read_csv(os.path.join(data_dir, 'norfolk_flooded_roads_data/STORM_data_flooded_streets_2010-2016_no_duplicates_clean.csv'))
all_flood_dates = flood_df._date.str.strip().unique()
flood_df.loc[:, '_date'] = pd.to_datetime(flood_df.loc[:, '_date'])
int_df = flood_df[flood_df.location == intersection_name]
int_flood_dates = int_df._date
events = int_df.event.str.split('(', expand=True)[0].str.strip()
events.reset_index(drop=True, inplace=True)
int_flood_dates.reset_index(drop=True, inplace=True)

subset_df = pd.read_csv(os.path.join(data_dir, 'downtown_nor_subset_points_data.txt'))
subset_locations = subset_df['location']
subset_floods = flood_df[flood_df['location'].isin(subset_locations)]
