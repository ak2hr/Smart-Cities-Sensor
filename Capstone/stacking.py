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

data = pd.read_csv("for_RF_model.csv") # reading csv file
#print("Original table dimensions:", data.shape)  # displaying data frame

# Add a LatLong column to the data to pair the Lat and Long data
data['Lat'] = data['Lat'].astype(str)
data['Long'] = data['Long'].astype(str)
data["LatLong"] = data["Lat"].map(str) + data["Long"]

#Shorten the table and use "chunking" to shorten the run time
shortTable = data[0:10]

#%%
# CREATING THE LOCATION TABLE

# Data frame of unique LatLong data
latlong = shortTable.filter(['Lat', 'Long'], axis=1) 
unlocation = latlong.groupby(['Lat', 'Long']).size().reset_index().rename(columns={0: 'count'}) 
Location = unlocation.drop(['count'], axis=1).reindex(columns=['Lat', 'Long', 'Street', 'Description'])
Location.insert(0, "location_ID", Location["Lat"].map(str) + Location["Long"])

#Test The uniqueness
#unlocation2 = Location.groupby(['LatLong']).size().reset_index().rename(columns={0:'count'})
#print(unlocation2[0:10])

# Open the SQLite connection
connection = sqlite3.connect("fdata.db", timeout=10)
cursor = connection.cursor()

#For each row, if the location is not already in the database insert into SQLite
for index, row in Location.iterrows():
    cursor.execute("SELECT location_ID FROM Locations WHERE location_ID = ?", (row['location_ID'],))
    match = cursor.fetchall()
    if len(match) == 0:
        cursor.execute('insert into locations values(?,?,?,?,?)', row)
        connection.commit()

connection.commit()

#%%
# CREATING THE TYPE TABLE

#drop un-needed columns
header = list(data) #list of column names in original dataset
droplist = ['OID_', 'Lat', 'Long', 'LatLong', 'event_date'] 
typetable = shortTable
for item in header:
    if item in droplist:
        typetable = typetable.drop(item, axis=1)

#For each type of statistic, insert it into the SQLite if it is not already in
        #the database. Asign its type_ID and description. 
statistic = list(typetable) #list of column names in new dataset
for stat in statistic:
    cursor.execute("SELECT Statistic FROM Types WHERE Statistic = ?", (stat,))
    statmatch = cursor.fetchall()
    if len(statmatch) == 0:
        if stat == ('rh' or 'max15' or 'hrs2' or 'hrs72'):
            cursor.execute('insert into types values(?,?,?)', (stat, stat, 'Rainfall'))
            connection.commit()
        elif stat == ('td_3av' or 'td_3l' or 'td_3h'):
            cursor.execute('insert into types values(?,?,?)', (stat, stat, 'Tide Level'))
            connection.commit()
        elif stat == ('AWDR' or 'AWND' or 'WGF6'):
            cursor.execute('insert into types values(?,?,?)', (stat, stat, 'Wind Speed'))
            connection.commit()
        elif stat == ('gw'):
            cursor.execute('insert into types values(?,?,?)', (stat, stat, 'Groundwater Level'))
            connection.commit()
        elif stat == ('f_nf'):
            cursor.execute('insert into types values(?,?,?)', (stat, stat, 'Flood Indicator'))
            connection.commit()
        else:
            cursor.execute('insert into types values(?,?,?)', (stat, stat, 'Topographic'))
            connection.commit()

connection.commit()

#%%
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

#%%
# CREATING THE VALUES TABLE

# Modify the original table to exclude OID, Long, and Lat
droplist2 = ['OID_', 'Lat', 'Long'] 
subTable = shortTable
for item in header:
    if item in droplist2:
        subTable = subTable.drop(item, axis=1)
#print(shortTable.shape)

# Stack the columns of the table using the melt function
        # The melt function creates a row for each datapoint and specifies its
        #type in a variable column
Values = pd.melt(subTable, id_vars=['event_date', 'LatLong'])
Values = Values.reindex(columns=['event_date', 'value', 'variable', 'LatLong'])
Values.rename(index=str, columns={"variable": "type_ID", "LatLong": "location_ID"})
#print(Values.head(10))
#print(Values.shape)

#For each row in the stacked dataset insert it into the database
for index, row in Values.iterrows():
    cursor.execute('insert into Vals values(?,?,?,?)', row)
    connection.commit()

connection.commit()
connection.close() #close the connection

#%%
## TESTING THE DATABASE

#connection = sqlite3.connect("fdata.db", timeout=10)
#cursor = connection.cursor()

# pd.read_sql_query("SELECT * FROM fevent", connection)

#connection.commit()
#connection.close()
