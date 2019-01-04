
# importing pandas module
import pandas as pd
import csv
import os
from datetime import datetime
from dateutil.parser import parse
import time
import string

# reading csv file
data = pd.read_csv("for_RF_model.csv")
# displaying  data frame
# print(data.head())
print("Original table dimensions:", data.shape)

################################################
# CREATING THE LOCATION TABLE

# Data frame of unique lat and long combinations
latlong = data.filter(['Lat', 'Long'], axis=1)
unlocation = latlong.groupby(['Lat','Long']).size().reset_index().rename(columns={0:'count'})
#unlocation2 = unlocation.groupby(['Lat','Long']).size().reset_index().rename(columns={0:'count'})
#print(unlocation[0:10])

# Creating location_ID
locationKey = list(range(len(unlocation)))
locationSeries = pd.Series(locationKey)
Location = unlocation.drop(['count'], axis=1).reindex(columns = ['Lat', 'Long', 'Street', 'Description'])
Location.insert(loc=0, column='location_ID', value=locationKey)
#print(Location[1:10])

#################################################
# CREATING THE TYPE TABLE

#################################################
# CREATING THE VALUES TABLE

# Modify the table to exclude OID, Long, and Lat
subTable = data.drop(['OID_'], axis=1)
shortTable = subTable[0:100000]
#print(subTable.shape)

# Stack the columns of the table using the melt function
Values = pd.melt(shortTable, id_vars=['event_date', 'Lat', 'Long'])
Values = Values.reindex(columns = ['event_date', 'Lat', 'Long', 'variable', 'value', 'location_ID'])

#The number of rows of the stacked table is now 15X the rows of the
#subtable because there were 15 columns stacked
print("Sub table dimensions:", shortTable.shape)
print("Values table dimensions:", Values.shape)

# Get the location id
location2 = Location
location2['Lat'] = location2['Lat'].astype(str)
location2['Long'] = location2['Long'].astype(str)
location2["LatLong"] = location2["Lat"].map(str) + location2["Long"]
print(location2[0:10])


Values['Lat'] = Values['Lat'].astype(str)
Values['Long'] = Values['Long'].astype(str)
Values["LatLong"] = Values["Lat"].map(str) + Values["Long"]



Values['location_ID'] = Values['location_ID'].map(location2.set_index('LatLong')['location_ID'])
print(Values[0:10])

# for index in Values.iterrows():
#     for locindex in Location.iterrows():
#         if Values['Lat'][index].equals(Location['Lat'][locindex]) and Values['Long'][index].equals(Location['Long'][locindex]):
#             Values['location_ID'][index] = Location['location_ID'][locindex]


listKey = list(range(len(data)))
seriesKey = pd.Series(listKey)
Values.insert(loc=0, column='value_ID', value=seriesKey)
#print(Values.head(1000))

#######################################################
# CONVERTING EVENT DATE TO datetime

# To read the csv file into python
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, "for_RF_model.csv")
data = pd.read_csv(path, sep=",")

print(data.head())
print(type(data['event_date'][0]))


data["event_date"] = data["event_date"] + ":00 2017"
saved_column = data.event_date
saved_column = saved_column.replace("_", " ")
print(saved_column.head())
for index,row in data.iterrows():
    if row['event_date'][0:5] == "March":
        datetime_ed = datetime.strptime(row['event_date'], "%B_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")
    elif row['event_date'][0:5] == "Aug18":
        row['event_date1'] = string.replace(row['event_date'],'Aug18', 'Aug')
        datetime_ed = datetime.strptime(row['event_date1'], "%b_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")
        #print(row['event_date'])
    else:
        datetime_ed = datetime.strptime(row['event_date'], "%b_%d_%H:%M %Y").strftime("%Y-%m-%d %H:%M")

#####################################################
## MAKING THE CONNECTION TO SQL SERVER
import sqlite3
connection = sqlite3.connect("fdata.db", timeout=10)

cursor = connection.cursor()

## Delete table to restart
#cursor.execute("""DROP TABLE fevent;""")

## Creating corresponding SQL table
sql_command = """
 CREATE TABLE fevent (
 value_ID INTEGER PRIMARY KEY,
 event_date VARCHAR(10),
 Lat DECIMAL,
 Long DECIMAL,
 variable VARCHAR(10),
 value FLOAT,
 location_ID VARCHAR(10),
 LatLong VARCHAR(50));"""
 #event_date --> DATE??? TIMESTAMP?
#
#cursor.execute(sql_command)
#print(len(Values))
c=list(zip(*[Values[col] for col in Values]))
#print(c[0])

for i in c:
 
 format_str = """INSERT INTO fevent (value_ID, event_date, Lat, Long, variable, value, location_ID, LatLong)
 VALUES (NULL, "{event_date}", "{Lat}", "{Long}", "{variable}", "{value}", "{location_ID}", "{LatLong}");"""
 sql_command = format_str.format(event_date=i[1], Lat=i[2], Long=i[3], variable=i[4], value = i[5], location_ID = i[6], LatLong=i[7])
 cursor.execute(sql_command)
 connection.commit()


##Testing: just putting in a row of 1's
#format_str = """INSERT INTO fevent (value_ID, event_date, Lat, Long, variable, value, location_ID, LatLong)
 #VALUES (NULL, "{event_date}", "{Lat}", "{Long}", "{variable}", "{value}", "{location_ID}", "{LatLong}");"""
#sql_command = format_str.format(event_date=2, Lat=2, Long=2, variable=2, value = 1, location_ID =1, LatLong=1)
#cursor.execute(sql_command)

#pd.read_sql_query("SELECT * FROM fevent", connection)

connection.commit()
connection.close()

