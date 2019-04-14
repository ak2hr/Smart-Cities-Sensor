#INSERTING CSV FILES INTO FLOOD EVENT DATABASE

# importing modules
import pandas as pd
import sqlite3
import csv
import os
from datetime import datetime
from dateutil.parser import parse
import time
import string

#read csv time: 12.62
read_csv_start = time.time()

data = pd.read_csv("for_RF_model.csv") # reading csv file

read_csv_end = time.time()
print("read csv time", read_csv_end - read_csv_start)

#quit()
#print("Original table dimensions:", data.shape)  # displaying data frame

# Add a LatLong column to the data to pair the Lat and Long data
data['Lat'] = data['Lat'].astype(str)
data['Long'] = data['Long'].astype(str)
data["LatLong"] = data["Lat"] + data["Long"]

#Shorten the table and use "chunking" to shorten the run time
shortTable = data[0:10]

# CONVERTING EVENT DATE TO datetime

"""shortTable["event_date"] = shortTable["event_date"] + ":00 2017"

for index,row in shortTable.iterrows():
    if row['event_date'][0:10] == "March":
        datetime_ed = datetime.strptime(row['event_date'], "%B_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")
    elif row['event_date'][0:10] == "Aug18":
        row['event_date'] = string.replace(row['event_date'],'Aug18', 'Aug')
        datetime_ed = datetime.strptime(row['event_date'], "%b_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")
    else:
        datetime_ed = datetime.strptime(row['event_date'], "%b_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")

shortTable.event_date = datetime_ed
print(shortTable.event_date.head())"""

#%%
# CREATING THE LOCATION TABLE 

location_start = time.time()

# Data frame of unique LatLong data
latlong = shortTable.filter(['Lat', 'Long'], axis=1) 
unlocation = latlong.groupby(['Lat', 'Long']).size().reset_index().rename(columns={0: 'count'}) 
Location = unlocation.drop(['count'], axis=1).reindex(columns=['location_ID', 'Lat', 'Long', 'Street', 'Description'])
Location.insert(1, "latlong", Location["Lat"].astype(str) + Location["Long"].astype(str))

#Test The uniqueness
#unlocation2 = Location.groupby(['LatLong']).size().reset_index().rename(columns={0:'count'})
#print(unlocation2[0:10])

# Open the SQLite connection
connection = sqlite3.connect("fdata.db", timeout=10)
cursor = connection.cursor()
#For each row, if the location is not already in the database insert into SQLite
for index, row in Location.iterrows():
    cursor.execute("SELECT latlong FROM Locations WHERE latlong = ?", (row['latlong'],))
    match = cursor.fetchall()
    if len(match) == 0:
        cursor.execute('INSERT INTO Locations values(?,?,?,?,?,?)', row)
        connection.commit()

connection.commit()
#connection.close()

location_end = time.time()
print("location time", location_end - location_start)

#%%
# CREATING THE TYPE TABLE

type_start = time.time()

#time with 10 rows, all new data: ~1.9 seconds 
#time with 100,000 rows, all new data: ~1.9 seconds
# row number doesnt matter
#dont think the time is significant in this table 

droplist = ['OID_', 'Lat', 'Long', 'LatLong', 'event_date'] 
typetable = shortTable
typetable = typetable.drop(droplist, axis=1)

# Open the SQLite connection
#connection = sqlite3.connect("fdata.db", timeout=10)
#cursor = connection.cursor()

#For each type of statistic, insert it into the SQLite if it is not already in
        #the database. Asign its type_ID and description. 
statistic = list(typetable) #list of column names in new dataset
for stat in statistic:
    cursor.execute("SELECT Statistic FROM Types WHERE Statistic = ?", (stat,))
    statmatch = cursor.fetchall()
    if len(statmatch) == 0:
        if stat == ('rh' or 'max15' or 'hrs2' or 'hrs72'):
            cursor.execute('insert into types values(?,?,?)', (None, stat, 'Rainfall'))
            connection.commit()
        elif stat == ('td_3av' or 'td_3l' or 'td_3h'):
            cursor.execute('insert into types values(?,?,?)', (None, stat, 'Tide Level'))
            connection.commit()
        elif stat == ('AWDR' or 'AWND' or 'WGF6'):
            cursor.execute('insert into types values(?,?,?)', (None, stat, 'Wind Speed'))
            connection.commit()
        elif stat == ('gw'):
            cursor.execute('insert into types values(?,?,?)', (None, stat, 'Groundwater Level'))
            connection.commit()
        elif stat == ('f_nf'):
            cursor.execute('insert into types values(?,?,?)', (None, stat, 'Flood Indicator'))
            connection.commit()
        else:
            cursor.execute('insert into types values(?,?,?)', (None, stat, 'Topographic'))
            connection.commit()

connection.commit()
#connection.close()

type_end = time.time()
print("type time", type_end - type_start)


#%%
# CREATING THE VALUES TABLE

# Open the SQLite connection
#connection = sqlite3.connect("fdata.db", timeout=10)
#cursor = connection.cursor()

vals_start = time.time()
#time with 100,000 rows, all new data: ~1.9 seconds

# Modify the original table to exclude OID, Long, and Lat
#header = list(shortTable)
droplist2 = ['OID_', 'Lat', 'Long'] 
subTable = shortTable
subTable = subTable.drop(droplist2, axis=1)
#print(shortTable.shape)

# Stack the columns of the table using the melt function
# The melt function creates a row for each datapoint and specifies its
#type in a variable column
Values = pd.melt(subTable, id_vars=['event_date', 'LatLong'])
Values = Values.reindex(columns=['vals_ID', 'event_date', 'value', 'variable', 'LatLong', 'type_ID', 'location_ID'])

#match the foriegn keys from the other two tables
for index, row in Values.iterrows():
    cursor.execute("SELECT location_ID FROM Locations WHERE latlong = ?", (row['LatLong'],))
    match = cursor.fetchall()
    a = match[0]
    Values.at[index, 'location_ID'] = a[0]
    connection.commit()
    cursor.execute("SELECT type_ID FROM Types WHERE statistic = ?", (row['variable'],))
    match2 = cursor.fetchall()
    b = match2[0]
    Values.at[index, 'type_ID'] = b[0]
    connection.commit()
connection.commit()

#delete the un-needed variable and latlong columns
Values = Values.drop(['variable', 'LatLong'], axis = 1)

#For each row in the stacked dataset insert it into the database
for index, row in Values.iterrows():
    cursor.execute('insert into Vals values(?,?,?,?,?)', row)
    connection.commit()

connection.commit()
connection.close() #close the connection

vals_end = time.time()
print("vals time", vals_end - vals_start)

#%%
## TESTING THE DATABASE
"""
connection = sqlite3.connect("fdata.db", timeout=10)
cursor = connection.cursor()

 pd.read_sql_query("SELECT * FROM fevent", connection)

connection.commit()
connection.close()
"""
