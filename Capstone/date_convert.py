# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 23:17:51 2019

@author: pc
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 22:58:16 2019

@author: pc
"""

import pandas as pd
import csv
import os
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import time
import string
import copy

# To read the csv file into python
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, "for_RF_modeltest_practice.csv")
data = pd.read_csv("C:/Users/pc/Downloads/for_RF_modeltest_practice (2).csv", sep=",")

# To create an empty column to write the new values in
data["datetime"] = ""

# Create new dataframe for datetime values
# To add mins: microseconds to the end of the event_date string
data["event_date"] = data["event_date"] + ":00:00:000000"
data["event_date"] = data["event_date"] + "_2017"
print(data["event_date"])
data2 = pd.DataFrame()
data2["event_date"] = data["event_date"]
data2["datetime"] = ""
print(data2["event_date"])


# Add year to the end of the "event_date" string

def date_convert(x):
    if x[0:5] == "March":  # If the first five character equal March
        datetime_ed = datetime.strptime(x, "%B_%d_%H:%M:%S:%f_%Y").strftime(
            "%Y-%m-%d %H:%M:%f")  # Parse the string containing March then formats into datetime format
        datetime_ed = datetime.strptime(datetime_ed,
                                        "%Y-%m-%d %H:%M:%f")  # Turns string of datetime format into datetime object
        # print(datetime_ed)
        return (datetime_ed)
        # data2["datetime"][x] = datetime_ed

    elif x[0:5] == "Aug18":  # If the first five character equal Aug18
        x = str.replace(x, "Aug18", "Aug")  # Change Aug18 to Aug for reformatting
        datetime_ed = datetime.strptime(x, "%b_%d_%H:%M:%S:%f_%Y").strftime(
            "%Y-%m-%d %H:%M:%f")  # Parse the string containing Aug then formats into datetime format
        datetime_ed = datetime.strptime(datetime_ed,
                                        "%Y-%m-%d %H:%M:%f")  # Turns string of datetime format into datetime object
        # print(datetime_ed)
        return (datetime_ed)
        # data2["datetime"][x] = datetime_ed
    else:
        datetime_ed = datetime.strptime(x, "%b_%d_%H:%M:%S:%f_%Y").strftime(
            "%Y-%m-%d %H:%M:%f")  # Parse the string containing every other value then formats into datetime format
        datetime_ed = datetime.strptime(datetime_ed,
                                        "%Y-%m-%d %H:%M:%f")  # Turns string of datetime format into datetime object
        # print(datetime_ed)
        return (datetime_ed)


for x in data2.index:
    data2["datetime"][x] = date_convert(data2["event_date"][x])

for x in data.index:
    data["datetime"][x] = date_convert(data["event_date"][x])

for x in data.index:
    data["datetime"][x] = str(date_convert(data["event_date"][x])) + str(x)

for x in data.index:
    print(str(date_convert(data["event_date"][x])) + str(x))
    
data.to_csv('C:\\Users\\pc\\Documents\\data.csv'),encoding='UTF-8')
