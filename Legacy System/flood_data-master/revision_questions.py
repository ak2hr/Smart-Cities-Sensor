
# coding: utf-8

# ## Intro

# There are a couple comments from the reviewers that I want to clear up in this notebook:
# 
# 1. How sensitive are the RF results to different parameter values such as number of trees? (from reviewer 1)
# 2. Why not just use rainfall as a proxy for flood severity? Why go to all the work of building these more complex model if most of the information just comes from the rainfall?
# 3. Not what the reviewers asked for but for my own peace of mind, are the two models being tested on the same data?

# In[1]:

get_ipython().magic(u'matplotlib inline')

from hr_db_scripts.main_db_script import get_db_table_as_df
from db_scripts.main_db_script import db_filename
from results import make_results_df
import pandas as pd


# In[2]:

def get_tables(table_suffix):


    rf_trn_tbl = 'rf{}train'.format(table_suffix)
    rf_tst_tbl = 'rf{}test'.format(table_suffix)
    ps_trn_tbl = 'poisson{}train'.format(table_suffix)
    ps_tst_tbl = 'poisson{}test'.format(table_suffix)

    rf_trn = get_db_table_as_df(rf_trn_tbl, dbfilename=db_filename)
    rf_tst = get_db_table_as_df(rf_tst_tbl, dbfilename=db_filename)
    ps_trn = get_db_table_as_df(ps_trn_tbl, dbfilename=db_filename)
    ps_tst = get_db_table_as_df(ps_tst_tbl, dbfilename=db_filename)
    return {'rf_trn': rf_trn, 'rf_tst': rf_tst, 'ps_trn': ps_trn, 'ps_tst': ps_tst}


# ### Question 3: are the models being tested on the same data?

# In[3]:

suffix = '_revisions_'
tables = get_tables(suffix)


# In[4]:

(tables['rf_trn']['all_trn'] != tables['ps_trn']['all_trn']).sum()


# In[5]:

(tables['rf_tst']['all_tst'] != tables['ps_tst']['all_tst']).sum()


# It looks like they weren't the same... Now we need to see how that affects the results

# ### Now the code has been refactored so they are the same

# In[6]:

suffix = '_revisions1_'
tables1 = get_tables(suffix)


# In[7]:

(tables1['rf_trn']['all_trn'] != tables1['ps_trn']['all_trn']).sum()


# In[8]:

(tables1['rf_tst']['all_tst'] != tables1['ps_tst']['all_tst']).sum()


# ### Question: do the results differ with the restructuring of the code?

# In[9]:

(tables1['rf_trn']['all_trn'] != tables['rf_trn']['all_trn']).sum()


# In[10]:

(tables1['rf_trn']['all_pred_trn'] != tables['rf_trn']['all_pred_trn']).sum()


# In[11]:

(tables1['rf_tst']['all_tst'] != tables['rf_tst']['all_tst']).sum()


# In[12]:

(tables1['ps_trn']['all_trn'] != tables['ps_trn']['all_trn']).sum()


# In[13]:

(tables1['ps_tst']['all_tst'] != tables['ps_tst']['all_tst']).sum()


# So now they are all the same

# ### Question #1 sensitivity to number of trees

# In[14]:

trees = [2, 5, 10, 17, 25, 35, 50, 100, 250, 350, 500, 650, 750, 1000, 2000]


# In[15]:

tables = {}


# In[16]:

for t in trees:
    tables[t] = 'rf_{}'.format(t)
tables[500] = 'revisions1'


# In[17]:

dfs = []
for t in tables:
    df = make_results_df(models=['rf'], suffix=tables[t])
    df.index = [t]
    dfs.append(df)
df_comb = pd.concat(dfs)


# In[18]:

df_comb.sort_index(inplace=True)
ax = df_comb.plot(style="o-", figsize = (9,7), logx=True, grid=True)
ax.legend(bbox_to_anchor=(1, 0.5))
ax.set_xlabel('Number of trees')


# In[19]:

ax = df_comb.rolling(5).mean().plot(style='o-', logx=True)
ax.legend(bbox_to_anchor=(1, 0.5))
ax.set_xlabel('Number of trees')


# ### Question #2 what if only rainfall

# In[20]:

suffixes = ['revisions1', 'only_rd', 'only_rain', 'no_rd', 'no_tides', 'top_5', 'top_2', 'revisions2', 'revisions2_no_tide']


# In[21]:

dfs = []
for s in suffixes:
    df = make_results_df(suffix=s)
    dfs.append(df)
    df.index = ["{}_{}".format(i, s) for i in df.index]
df_vars = pd.concat(dfs)

    


# In[22]:

df_vars


# In[23]:

(21.41-17.82)/21.41


# In[24]:

(21.41-20.49)/21.41


# In[25]:

(24.95-21.41)/21.41


# In[26]:

ax = df_vars.plot.bar(figsize=(8,6))
ax.legend(bbox_to_anchor=(1, 0.5))


# ### Sensitivity to number of variables

# In[27]:

suffixes = [4, 6, 8, 10, 12, 14, 18, 20]
suffixes = ['rf_{}v'.format(i) for i in suffixes]


# In[28]:

dfs = []
for s in suffixes:
    df = make_results_df(suffix=s, models=['rf'])
    dfs.append(df)
    df.index = ["{}_{}".format(i, s) for i in df.index]
df_nvars = pd.concat(dfs)

    


# In[29]:

df_nvars


# In[30]:

ax = df_nvars.plot(figsize=(8,6))
ax.legend(bbox_to_anchor=(1, 0.5))


# In[31]:

df_tune = get_db_table_as_df("tuning_mtry", dbfilename=db_filename)


# In[32]:

del df_tune['row_names']


# In[33]:

df_tune_piv = df_tune.pivot(columns="mtry", values="OOBError")
df_tune_piv.mean().plot.bar()


# In[34]:

j = 0
l = []
m = []
first_time = True
for i in df_tune.iterrows():
    if i[1]['mtry'] == 1 and first_time == False:
        sub_df = pd.DataFrame(m)
        sub_df['num_run'] = j
        sub_df['rank'] = sub_df['OOBError'].rank()
        l.append(sub_df)
        j += 1
        m = []
    first_time = False
    m.append(i[1])


# In[35]:

df_tune_counts = pd.concat(l)


# In[36]:

df_tune_counts.head()


# In[37]:

df_tune_rank_pivot = df_tune_counts.pivot_table(values='rank', columns='num_run', index='mtry')


# In[38]:

df_tune_rank_pivot.head(6)


# In[39]:

(df_tune_rank_pivot == 1).sum(1).plot.bar()


# ## number of predictions outside 159 poisson

# In[40]:

suffix = '_revisions2_'
tables_rev2 = get_tables(suffix)


# In[41]:

tables_rev2


# In[42]:

ps_prd = tables_rev2['ps_tst']['all_pred_tst']


# Percent above 159

# In[43]:

(ps_prd > 159).sum()/float(len(ps_prd)) * 100


# Percent above 159 when prediction is at least 0.5 (rounds to 1)

# In[44]:

(ps_prd > 159).sum()/float((ps_prd>0.5).sum()) * 100


# ### predictions when true flooding is 31

# In[52]:

ps_tst = tables_rev2['ps_tst']
pred_31 = ps_tst[(ps_tst['all_tst']==31) & (ps_tst['all_pred_tst']<159)]['all_pred_tst']
print pred_31.mean()
print pred_31.max()
print pred_31.min()


# In[ ]:



