import numpy as np
import pandas as pd


def percentile(df):
    df['val_percentile'] = (df.Value.rank()/max(df.Value.rank()))*100
    return df


def rank(df):
    df['val_rank'] = max(df.Value.rank()) + 1 - df.Value.rank()
    return df


def normalize(df):
    max_val = df.Value.max()
    min_val = df.Value.min()
    val_range = max_val - min_val
    df['scaled'] = (df.Value-min_val)/val_range
    return df


def resample_df(df, agg_typ):
    ori_df = df
    if agg_typ == 'mean':
        df = df.resample('D').mean()
    elif agg_typ == 'max':
        df = df.resample('D').max()
    elif agg_typ == 'min':
        df = df.resample('D').min()
    elif agg_typ == 'sum':
        df = df.resample('D').sum()
    df['SiteID'] = ori_df.SiteID[0]
    df['VariableID'] = ori_df.VariableID[0]
    return df


def account_for_elev(df, elev_threshold=10, col='Value'):
    cleaned = np.where(df[col] > elev_threshold, np.nan, df[col])
    df[col] = cleaned
    return df


def hampel_filter(df, col, k, threshold=2):
    rolling_median = df[col].rolling(k).median()
    rolling_std = df[col].rolling(k).std()
    num_sigma = abs(df[col]-rolling_median)/rolling_std
    df[col] = np.where(num_sigma > threshold, rolling_median, df[col])
    return df




