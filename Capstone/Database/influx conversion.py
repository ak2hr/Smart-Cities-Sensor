import pandas as pd
import sqlite3
import csv
import os
from datetime import datetime
from dateutil.parser import parse
import time
import string

start = time.time()
#read csv time: 12.62
read_csv_start = time.time()

data = pd.read_csv("for_RF_model.csv") # reading csv file

read_csv_end = time.time()
print("read csv time", read_csv_end - read_csv_start)


#%%
shortTable = data[0:10]
shortTable[['Lat', 'rh']]

data = data.drop("OID_", axis=1)
measurement = list(data)
measurement

shortTable['Lat']

#this is the format of the measurment tables that need to be inserted to the influx measurements
rh = pd.DataFrame({'time': data['event_date'],
                   'lat': data['Lat'],
                   'long': data['Long'],
                   'f_nf': data['f_nf'],
                   'value': data['rh']})

rh = rh.set_index('date_time')


