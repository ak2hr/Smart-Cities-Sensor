
# coding: utf-8

# In[1]:

import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from hr_db_scripts.main_db_script import get_db_table_as_df
from main_db_script import db_filename
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


# In[2]:

def indicies_where_daily_rain_exceeds_threshold(df, threshold):
    rd = df[[c for c in df.columns if c.startswith('rd')]]
    ind_abv_threshold = rd[rd.max(axis=1)>0.1].index
    return ind_abv_threshold


# In[3]:

flood_locations = get_db_table_as_df('flood_locations', dbfilename=db_filename)
flood_events = get_db_table_as_df('flood_events', date_col=['event_date', 'dates'], dbfilename=db_filename)
for_model = get_db_table_as_df('for_model', date_col=['event_date'], dbfilename=db_filename)
daily_obs = get_db_table_as_df('nor_daily_observations', date_col=['Datetime'], dbfilename=db_filename)


# In[4]:

print flood_locations.shape
flood_locations = flood_locations[flood_locations.in_hague==1]
print flood_locations.shape
flood_locations.head()


# In[5]:

daily_obs.set_index('Datetime', inplace=True)


# In[6]:

print daily_obs.shape
rain_threshold = 0.1
rd_abv_thresh = indicies_where_daily_rain_exceeds_threshold(daily_obs, rain_threshold)


# In[7]:

daily_obs = daily_obs.loc[rd_abv_thresh,:]
print daily_obs.shape
daily_obs.head()


# In[8]:

flood_events.head()


# In[9]:

for_model.set_index('event_date', inplace=True)
for_model.shape


# In[10]:

for_model = for_model.loc[indicies_where_daily_rain_exceeds_threshold(for_model, rain_threshold),:]
print for_model.shape
for_model.head()


# In[11]:

print flood_locations.shape
flood_locations = flood_locations[flood_locations['count']>1]
flood_locations.shape


# In[12]:

lst = []
for index, row in flood_locations.iterrows():
    l = row['location'].strip()
    loc_data = daily_obs.copy()
    loc_data['flooded'] = 0
    if l != '':
        event_dates = flood_events[flood_events['location'] == l]['event_date']
        all_fld_dates = flood_events[flood_events['event_date'].isin(event_dates)]['dates']
        all_fld_dates = np.append(all_fld_dates, event_dates)
        all_fld_dates = pd.to_datetime(np.unique(all_fld_dates))

        fld_data = for_model[for_model.index.isin(event_dates)]
    
        loc_data = loc_data[~loc_data.index.isin(all_fld_dates)]
        loc_data = pd.concat([loc_data, fld_data])
    
        # add geog data
    for k in row.keys():
        loc_data[k] = row[k]
    lst.append(loc_data)
#         print l
#         print loc_data.head()
        


# In[13]:

all_locations = pd.concat(lst)
all_locations.reset_index(inplace=True)


# In[14]:

all_locations.shape
all_locations.head()


# In[15]:

del all_locations['level_0']
all_locations.tail()


# In[16]:

x_train, x_test, y_train, y_test = train_test_split(all_locations.index, all_locations.flooded, test_size=0.3, stratify=all_locations.flooded)


# In[17]:

x_train_fld = all_locations.index[(all_locations.index.isin(x_train)) & (all_locations.flooded==True)]
# x_train_fld = all_locations.index[all_locations.flooded==True]
x_train_nfld = all_locations.index[(all_locations.index.isin(x_train)) & (all_locations.flooded==False)]
x_train_nfld_sampled = np.random.choice(x_train_nfld, size=len(x_train_fld)*5)
x_train_combined = np.concatenate((x_train_fld, x_train_nfld_sampled))
train_data = all_locations.loc[x_train_combined, :]
train_data = all_locations.loc[x_train, :]


# In[18]:

test_data = all_locations.loc[x_test, :]


# In[19]:

print [a.shape for a in [x_train_fld, x_train_nfld,x_train_combined,train_data,test_data]]


# In[20]:

con = sqlite3.connect(db_filename)
train_data.to_sql(con=con, name='train_geog_data_hg', if_exists='replace')
test_data.to_sql(con=con, name='test_geog_data_hg', if_exists='replace')


# In[ ]:



