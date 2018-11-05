# coding: utf-8
import matplotlib.pyplot as plt
from hr_db_scripts.main_db_script import get_df_for_dates
from db_scripts.main_db_script import fig_dir
import pandas as pd


def plot_rain_tide(start_date, end_date):
    evrain = get_df_for_dates('rainfall', start_date, end_date)
    evrain = evrain.mean(axis=1)
    evrain.rename('cummulative rainfall (in)', inplace=True)
    evtide = get_df_for_dates('six_min_tide', start_date, end_date).resample('15T').mean()
    evtide = evtide.mean(axis=1)
    evtide.rename('tide (ft abv msl)', inplace=True)
    evgw = get_df_for_dates('shallow_well_depth', start_date, end_date).resample('15T').mean()
    evgw = evgw.mean(axis=1)
    evgw.rename('gw (ft abv NAVD 88)', inplace=True)
    evrainc = evrain.cumsum()

    y_label = 'Tide Level (ft above MSL)/\nCumulative Rainfall (in)'
    x_label = 'Date'
    ax = pd.concat([evrainc, evtide, evgw], axis=1).plot()
    ax.set_xlabel(x_label)
    ax.set_ylim(ymin=0, ymax=13)
    plt.tight_layout()
    plt.savefig("{}event_plot_gw{}".format(fig_dir, start_date), dpi=300)

hr_dates = ['2016-09-02',  '2016-09-05']
plot_rain_tide(*hr_dates)
th_dates = ['2013-10-08', '2013-10-11']
plot_rain_tide(*th_dates)
matth_dates = ['2016-10-08', '2016-10-11']
plot_rain_tide(*matth_dates)
jqn_dates = ['2015-09-30', '2015-10-05']
plot_rain_tide(*jqn_dates)
unknown_dates = ['2011-10-28', '2011-10-30']
plot_rain_tide(*unknown_dates)
