import matplotlib.pyplot as plt
from flood_data.project_db_scripts.get_server_data import data_dir
import pandas as pd


def plot_flooded(dates):
    num_subplots = 20
    for i in range(len(dates)/num_subplots):
        fig, axs = plt.subplots(5, 4, sharex=True, sharey=True, figsize=(6.5, 6.5))
        axs = axs.ravel()
        for j in range(min(num_subplots, len(dates) - num_subplots * i)):
            plot_df = df[df['_date'] == dates.index[j + i * num_subplots]]
            axs[j].scatter(plot_df['xcoord']/1000., plot_df['ycoord']/1000.)
            plt.xticks(rotation=90)
        plt.show()
df = pd.read_csv('{}/norfolk_flooded_roads_data/STORM_data_flooded_streets_2010-2016_no_duplicates_clean.csv'.format(data_dir))
date_value_counts = df['_date'].value_counts()
dates_above_median = date_value_counts[date_value_counts>date_value_counts.median()]

