# importing pandas module
import pandas as pd
import sqlite3
import csv
import os
from datetime import datetime
from dateutil.parser import parse
import time
import string

# reading csv file
data = pd.read_csv("for_RF_model.csv")
# displaying  data frame
#print(data.head())
print("Original table dimensions:", data.shape)

# Add a LatLong column to the data to pair the Lat and Long data
data['Lat'] = data['Lat'].astype(str)
data['Long'] = data['Long'].astype(str)
data["LatLong"] = data["Lat"].map(str) + data["Long"]

#Using chunking to shorten the run time
shortTable = data[0:10]

###############################################################################
# CREATING THE LOCATION TABLE

# Data frame of unique LatLong data
latlong = shortTable.filter(['Lat', 'Long'], axis=1)
unlocation = latlong.groupby(['Lat', 'Long']).size().reset_index().rename(columns={0: 'count'})
Location = unlocation.drop(['count'], axis=1).reindex(columns=['Lat', 'Long', 'Street', 'Description'])
Location.insert(0, "LatLong", Location["Lat"].map(str) + Location["Long"])

#Test The uniqueness
#unlocation2 = Location.groupby(['LatLong']).size().reset_index().rename(columns={0:'count'})
#print(unlocation2[0:10])

#### If the location is not already in the database insert into SQLite
connection = sqlite3.connect("fdata.db", timeout=10)
cursor = connection.cursor()

for index, row in Location.iterrows():
    cursor.execute("SELECT LatLong FROM locations WHERE LatLong = ?", (row['LatLong'],))
    match = cursor.fetchall()
    if len(match) == 0:
        cursor.execute('insert into locations values(?,?,?,?,?)', row)
        connection.commit()

connection.commit()


#################################################
# CREATING THE TYPE TABLE

typetable = shortTable.drop(['OID_', 'Lat', 'Long', 'LatLong', 'event_date'], axis=1)
statistic = list(typetable)
description = list()

#types = pd.DataFrame({'Statistic':statistic, 'Description': description})


for stat in statistic:
    cursor.execute("SELECT Statistic FROM types WHERE Statistic = ?", (stat,))
    statmatch = cursor.fetchall()
    if len(statmatch) == 0:
        if stat == ('rh' or 'max15' or 'hrs2' or 'hrs72'):
            cursor.execute('insert into types values(?,?)', (stat, 'Rainfall'))
            connection.commit()
        elif stat == ('td_3av' or 'td_3l' or 'td_3h'):
            cursor.execute('insert into types values(?,?)', (stat, 'Tide Level'))
            connection.commit()
        elif stat == ('AWDR' or 'AWND' or 'WGF6'):
            cursor.execute('insert into types values(?,?)', (stat, 'Wind Speed'))
            connection.commit()
        elif stat == ('gw'):
            cursor.execute('insert into types values(?,?)', (stat, 'Groundwater Level'))
            connection.commit()
        elif stat == ('f_nf'):
            cursor.execute('insert into types values(?,?)', (stat, 'Flood Indicator'))
            connection.commit()
        else:
            cursor.execute('insert into types values(?,?)', (stat, 'Topographic'))
            connection.commit()

connection.commit()
connection.close()


#################################################
# CREATING THE VALUES TABLE

# Modify the table to exclude OID, Long, and Lat
subTable = data.drop(['OID_', 'LatLong'], axis=1)
shortTable = subTable[0:10]
# print(subTable.shape)

# Stack the columns of the table using the melt function
Values = pd.melt(shortTable, id_vars=['event_date', 'Lat', 'Long'])
Values = Values.reindex(columns=['event_date', 'Lat', 'Long', 'variable', 'value', 'location_ID'])

# The number of rows of the stacked table is now 15X the rows of the
# subtable because there were 15 columns stacked
#print("Sub table dimensions:", shortTable.shape)
#print("Values table dimensions:", Values.shape)

# Get the location id
#location2 = Location
#location2['Lat'] = location2['Lat'].astype(str)
#location2['Long'] = location2['Long'].astype(str)
#location2["LatLong"] = location2["Lat"].map(str) + location2["Long"]
#print(location2[0:10])

Values['Lat'] = Values['Lat'].astype(str)
Values['Long'] = Values['Long'].astype(str)
Values["LatLong"] = Values["Lat"].map(str) + Values["Long"]

#Values['location_ID'] = Values['location_ID'].map(location2.set_index('LatLong')['location_ID'])
#print(Values[0:10])

listKey = list(range(len(data)))
seriesKey = pd.Series(listKey)
Values.insert(loc=0, column='value_ID', value=seriesKey)
# print(Values.head(1000))

#######################################################
# CONVERTING EVENT DATE TO datetime

# To read the csv file into python
#dirname = os.path.dirname(__file__)
#path = os.path.join(dirname, "for_RF_model.csv")
#data = pd.read_csv(path, sep=",")

#print(data.head())
#print(type(data['event_date'][0]))

#data["event_date"] = data["event_date"] + ":00 2017"
#saved_column = data.event_date
#saved_column = saved_column.replace("_", " ")
#print(saved_column.head())
#for index, row in data.iterrows():
    #if row['event_date'][0:5] == "March":
        #datetime_ed = datetime.strptime(row['event_date'], "%B_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")
    #elif row['event_date'][0:5] == "Aug18":
        #row['event_date1'] = string.replace(row['event_date'], 'Aug18', 'Aug')
        #datetime_ed = datetime.strptime(row['event_date1'], "%b_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")
        # print(row['event_date'])
    #else:
        #datetime_ed = datetime.strptime(row['event_date'], "%b_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")

#####################################################
## MAKING THE CONNECTION TO SQL SERVER
connection = sqlite3.connect("fdata.db", timeout=10)

cursor = connection.cursor()

# print(len(Values))
c = list(zip(*[Values[col] for col in Values]))
# print(c[0])

for i in c:
    format_str = """INSERT INTO fevent (value_ID, event_date, Lat, Long, variable, value, location_ID, LatLong)
 VALUES (NULL, "{event_date}", "{Lat}", "{Long}", "{variable}", "{value}", "{location_ID}", "{LatLong}");"""
    sql_command = format_str.format(event_date=i[1], Lat=i[2], Long=i[3], variable=i[4], value=i[5], location_ID=i[6],
                                    LatLong=i[7])
    cursor.execute(sql_command)
    connection.commit()

##Testing: just putting in a row of 1's
# format_str = """INSERT INTO fevent (value_ID, event_date, Lat, Long, variable, value, location_ID, LatLong)
# VALUES (NULL, "{event_date}", "{Lat}", "{Long}", "{variable}", "{value}", "{location_ID}", "{LatLong}");"""
# sql_command = format_str.format(event_date=2, Lat=2, Long=2, variable=2, value = 1, location_ID =1, LatLong=1)
# cursor.execute(sql_command)

# pd.read_sql_query("SELECT * FROM fevent", connection)

connection.commit()
connection.close()
