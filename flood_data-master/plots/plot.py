import os
import sys
directory = os.path.dirname(__file__)
sys.path.insert(0, 'C:/Users/jeff/Documents/research/Sadler_3rdPaper/flood_data')
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from db_scripts.get_server_data import Variable, fig_dir, get_table_for_variable
from matplotlib import rcParams
import numpy as np
import math
from db_scripts.data_utils import resample_df, normalize, rank, percentile, filter_df_by_dates
from norfolk_flood_data.focus_intersection import int_flood_dates
from mpl_toolkits.mplot3d import Axes3D
from datetime import timedelta
cols = '#a6cee3', '#d95f02', '#1f78b4'


def get_plottable_df(variable_id, agg_typ, site_id=None, dates=int_flood_dates):
    df = get_table_for_variable(variable_id)
    if site_id:
        df = df[df.SiteID == site_id]
    df = resample_df(df, agg_typ)

    if variable_id == 5:
        # take out days with no rain
        df = df[df.Value != 0]

    df = normalize(df)
    df = rank(df)
    df = percentile(df)
    df = filter_df_by_dates(df, dates)
    df['Value'].fillna(0, inplace=True)
    return df


def plot_indiv_variable(variable_id, agg_typ, site_id=None, plt_var='value', dates=int_flood_dates, **kwargs):
    """
    plots bar charts for a given variable given a list of dates
    :param plot:
    :param plt_var:
    :param variable_id: 4-tide level, 5-rainfall, 6-shallow well depth
    :param agg_typ: how to aggregate the data on the daily time step ('min', 'max', 'mean', 'sum')
    :param site_id: site_id on which to filter (mostly for rainfall since there are multiple gauges
    :param dates: list of dates for which you want the plot
    :return:
    """
    df = get_plottable_df(variable_id, agg_typ, site_id, dates)
    v = Variable(variable_id)
    if variable_id == 4:
        c = cols[0]
    elif variable_id == 6:
        c = cols[1]
    elif variable_id == 5:
        c = cols[2]
    else:
        c = 'blue'

    if plt_var == 'scaled':
        col = 'scaled'
        units = 'Scaled'
    elif plt_var == 'rank':
        col = 'val_rank'
        units = v.units
    elif plt_var == 'value':
        col = 'Value'
        units = v.units
    else:
        raise ValueError('I do not know what variable to plot')
    fig, ax0 = plot_bars(df, col, v.variable_name, agg_typ, units, color=c, **kwargs)
    if variable_id == 4:
        plot_indicator_line(ax0, 3.2, units="ft")
    return fig, ax0


def plot_indicator_line(ax, val, label="", units="", **kwargs):
    xlims = ax.get_xlim()
    ax.plot(xlims, (val, val), 'r-', **kwargs)
    lab = "{} {}".format(val, units) if not label else label
    ax.text(xlims[0], val+val*0.01, lab)
    return ax


def save_plot(fig, variable_name, col, **kwargs):
    fig.tight_layout()
    file_dir = kwargs.get('file_dir', fig_dir)
    file_name = kwargs.get('file_name', '{}_{}'.format(variable_name, col))
    plt.savefig("{}{}.png".format(file_dir, file_name), dpi=300)
    plt.close()


def autolabel(ax, rects, labs):
    # attach some text labels
    i = 0
    for rect in rects:
        height = rect.get_height()
        height = 0 if math.isnan(height) else height
        try:
            label = int(labs[i])
        except ValueError:
            if math.isnan(labs[i]):
                label = 'NA'
            else:
                label = 'unknown'
        ax.text(rect.get_x()+rect.get_width()/2, 0.1+height, label, rotation=75, ha='center',
                va='bottom')
        i += 1


def plot_bars(df, col, variable_name, agg_typ, units, color='blue', fontsize=10, figsize=(5, 4), legend_plot=False, **kwargs):
    print "making figure for ", variable_name
    fig = plt.figure(figsize=figsize)
    ind = np.arange(len(df.index))
    if legend_plot:
        gs = gridspec.GridSpec(2, 2, width_ratios=[3.5, 1], height_ratios=[1, 1])
        ax0 = plt.subplot(gs[:, 0])
        ax1 = plt.subplot(gs[-1])
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.xaxis.set_ticklabels([])
        ax1.yaxis.set_ticklabels([])
        ax1.text(0.5, 0.5, "percentile",
                 multialignment='center', rotation=20, ha='center', va='bottom')
        ax1.set_title('Legend')
        width = 0.5
        ax1.bar((1 - width) / 2, 0.5, width=width, color=color)
    else:
        ax0 = fig.add_subplot(111)
    bars = ax0.bar(ind, df[col], color=color)
    autolabel(ax0, bars, df.val_percentile)
    ax0.set_xticks(ind+0.5)
    # ax0.set_xticklabels(events, rotation=90)
    ax0.set_xticklabels(df.index.strftime("%Y-%m-%d"), rotation=90)
    for label in ax0.get_xticklabels():
        if label._text in str(int_flood_dates):
            label._fontproperties._weight = 'bold'
    ax0.set_ylabel(units)
    ax0.set_xlabel('Event Date')
    ax0.set_xlim(0, len(ind))
    ax0.set_ylim(ymax=df[col].max()*1.1)
    ax0.set_title("{}: {}".format(variable_name, agg_typ), fontsize=fontsize)

    rcParams.update({'font.size': fontsize})
    return fig, ax0


def all_plottable_dfs(site_id=None):
    plot_tide_data = get_plottable_df(4, 'max')
    plot_gw_data = get_plottable_df(6, 'mean')
    plot_rain_data = get_plottable_df(5, 'sum', site_id=site_id)
    return plot_tide_data, plot_gw_data, plot_rain_data


def plot_all_separately(**kwargs):
    variables = [(4, 'max'), (6, 'mean'), (5, 'sum')]
    for v in variables:
        fig, ax0 = plot_indiv_variable(*v, plt_var='value')
        save_plot(fig, Variable(v[0]).variable_name, 'value')


def plot_together(col='Value'):
    df_list = all_plottable_dfs()
    i = 0
    fig, ax = plt.subplots(figsize=(8, 4.5))
    global cols
    for df in df_list:
        v = Variable(df.VariableID.dropna()[0])
        size = 2
        ind = np.arange(0, len(df.index)*size, size) + i*size*.25
        if v.variable_name == "Shallow Well Depth in NAVD88":
            label = "Shallow Well Depth"
        else:
            label = v.variable_name
        label += ' [{}]'.format(v.units)
        ax.bar(ind, df[col], label=label, color=cols[i], width=size*.25, linewidth=0.25)
        i += 1
    # ax.set_ylim(0, 110)
    ax.set_xlim(0, len(ind)*size)
    if col == 'val_percentile':
        ylab = 'percentile'
    elif col == 'Value':
        ylab = 'Value'
    else:
        ValueError('I do not know what the ylabel should be')
    ax.set_ylabel(ylab)
    ax.set_xlabel('Event Date')
    ax.set_xticks(ind-.25*size)
    # ax.set_xticklabels(events, rotation=90, ha='left')
    ax.set_xticklabels(df.index.strftime("%Y-%m-%d"), rotation=90, ha='left')
    plot_indicator_line(ax, 3.23, label=" ")
    rcParams.update({'font.size': 11})
    lgd = ax.legend(bbox_to_anchor=(0.1, -.4), loc='upper center', fontsize=11)
    fig.tight_layout()
    fig.savefig("{}all_{}_dates.png".format(fig_dir, col),
                dpi=300,
                bbox_extra_artists=(lgd,),
                bbox_inches='tight')


def plot_3d():
    plot_tide_data, plot_gw_data, plot_rain_data = all_plottable_dfs()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x0 = plot_tide_data.val_percentile
    x1 = plot_gw_data.val_percentile
    x2 = plot_rain_data.val_percentile
    ax.scatter(x0, x1, x2)
    ax.set_xlabel('Tide Percentile')
    ax.set_ylabel('Shallow Well Percentile')
    ax.set_zlabel('Rainfall Percentile')
    ax.set_xlim(100, 0)
    plt.show()


def plot_rain_sites(site_ids):
    for i in site_ids:
        plot_indiv_variable(5,
                             'sum',
                            site_id=i,
                            plot=True,
                            file_name='rain_site{}'.format(i)
                            )


def plot_time_series(variable_id, filt=True):
    df = get_table_for_variable(variable_id)
    # df['Value'] = np.where(df.index > "2015-09-23", df['Value']-0.85, df['Value'])
    fig, ax = plt.subplots()
    ax.plot(df['Value'])
    ax.set_xlabel('Date')
    ax.set_ylabel('Shallow well depth (ft above NAVD88)')
    plt.xticks(rotation=90)
    plot_indicator_line(ax, 1.85)
    plot_indicator_line(ax, 0.85)
    fig.tight_layout()
    plt.show()


def plot_surrounding_dates(plus_or_minus_days):
    new_dates = int_flood_dates
    for i in range(plus_or_minus_days):
        # plus_one_day = int_flood_dates + timedelta(days=i + 1)
        minus_one_day = int_flood_dates + timedelta(days=-i - 1)
        new_dates = pd.concat([new_dates, minus_one_day])
    new_dates.drop_duplicates(inplace=True)
    new_dates.sort_values(inplace=True)
    fig, ax0 = plot_indiv_variable(5, 'sum', site_id=6, plot=True, dates=new_dates,
                        fontsize=13, figsize=(15, 7))
    fig.add_axes(ax0)
    fig.tight_layout()
    fig.savefig('{}/rainfall_previous_days.png'.format(fig_dir), dpi=300)
    plt.show()
    print 'test'


def main():
    # all_plottable_dfs(plot=True)
    # plot_together()
    # get_plottable_df(5, 'sum', site_id=6)
    plot_time_series(6)
    # plot_all_separately()
    # plot_surrounding_dates(3)


if __name__ == "__main__":
    main()

