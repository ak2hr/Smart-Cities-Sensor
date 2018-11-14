
# coding: utf-8

# In[1]:

get_ipython().magic(u'matplotlib inline')
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.svm import SVR
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_predict
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from db_scripts.main_db_script import db_filename
from hr_db_scripts.main_db_script import get_db_table_as_df
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# In[2]:

df = get_db_table_as_df('for_model_avgs', dbfilename=db_filename)


# In[3]:

print df.shape
df = df[df.rd>0.01]
df.shape


# In[4]:

out_col = 'num_flooded'
in_cols = [a for a in df.columns if a not in ['event_date', 'event_name', out_col]]


# In[5]:

df[in_cols]
df = df[pd.isnull(df[in_cols]).sum(1)==0]
df.shape


# In[6]:

reg = RandomForestRegressor(oob_score=True, n_estimators=1000, max_features=0.33)
reg.fit(df[in_cols], df[out_col])


# In[7]:

preds = reg.predict(df[in_cols])
print r2_score(df.num_flooded, preds)
print mean_absolute_error(df.num_flooded, preds)
print mean_squared_error(df.num_flooded, preds)


# In[8]:

maxval = df[out_col].max()
fig, ax = plt.subplots(1)
ax.plot([0,180], [0,180], c='gray', lw=1)
ax.scatter(df.num_flooded, preds, facecolors='none', edgecolors='royalblue', marker='v', label='Training')
ax.scatter(df.num_flooded, reg.oob_prediction_, marker='o', facecolors='none', edgecolors='sienna', label='Out of bag')
ax.legend(frameon=False)
ax.set_aspect('equal', adjustable='box-forced')
ax.set_xticks(np.arange(0, maxval*2, 25))
ax.set_yticks(np.arange(0, maxval*2, 25))
ax.set_xlim((0, maxval*1.05))
ax.set_ylim((0, maxval*1.05))


# In[9]:

pd.Series(data=reg.feature_importances_, index=in_cols).sort_values(ascending=False).plot.bar()


# In[10]:

print r2_score(df.num_flooded, reg.oob_prediction_)
print mean_absolute_error(df.num_flooded, reg.oob_prediction_)
print mean_squared_error(df.num_flooded, reg.oob_prediction_)


# ## Cross validation

# In[11]:

bins = np.linspace(0, 110, 6)


# In[12]:

bins


# In[13]:

y_binned = np.digitize(df[out_col], bins)


# In[14]:

pd.Series(y_binned, dtype='category').value_counts()


# In[15]:

x_train, x_test, y_train, y_test = train_test_split(df[in_cols], df[out_col], stratify = y_binned, test_size = 0.3)


# In[16]:

C_range = np.logspace(-2, 10, 13)
gamma_range = np.logspace(-9, 3, 13)
param_grid = dict(gamma=gamma_range, C=C_range)
grid = GridSearchCV(SVR(), param_grid=param_grid)
grid.fit(x_train, y_train)


# In[17]:

grid


# In[18]:

'try'


# In[19]:

a = 't'


# In[ ]:



