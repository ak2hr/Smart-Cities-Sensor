
# importing pandas module
import pandas as pd

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

# #Replace underscores with blank spaces
# data["event_date"] = data["event_date"] + ":00 2017"
# saved_column = data.event_date
# #saved_column = saved_column.replace("_", " ")
# #mystring.replace("_", " ")
# print(saved_column.head())
# for index row in data.iterrows():
#     datetime.strptime(row, "%b_%d_%H%M %Y").strftime("%Y-%m-%d %H:%M")

#Convert Event date string into a datetime string
#datetime.strptime(saved_column, "%b %d %H%M %Y").strftime("%Y-%m-%d %H:%M")
#conv =time.strptime(saved_column, "%b %d %H%M %Y")
#time.strftime("%Y-%m-%d %H:%M", conv)
#Convert Datetime String to Datetime
#datetime_object = datetime.strptime((?), '%Y-%m-%d %H:%M')

#####################################################
## MAKING THE CONNECTION TO SQL SERVER

#print(valuesTable.value_ID.dtype) --> float64
#print(valuesTable.event_date.dtype) --> object
#print(valuesTable.variable.dtype) --> object
#print(valuesTable.value.dtype) --> float64

import sqlite3
connection = sqlite3.connect("for_RF.db")

cursor = connection.cursor()

## Delete table to restart
#cursor.execute("""DROP TABLE event;""")

## Creating corresponding SQL table
sql_command = """
 CREATE TABLE fevent (
 value_ID FLOAT PRIMARY KEY,
 event_date VARCHAR(10),
 Lat DECIMAL,
 Long DECIMAL,
 variable VARCHAR(10),
 value FLOAT,
 location_ID VARCHAR(10)
 LatLong VARCHAR(50));"""
 #event_date --> DATE??? TIMESTAMP?
#
cursor.execute(sql_command)
#
for p in Values:
    format_str = """INSERT INTO fevent (value_ID, event_date, Lat, Long, variable, value, location_ID, LatLong)
    VALUES ("{value_ID}", "{event_date}", "{Lat}", "{Long}", "{variable}", "{value}", "{location_ID}", "{LatLong}");"""

    sql_command = format_str.format(value_ID=p[0], event_date=p[1], Lat=p[2], Long=p[3], variable=p[4], value = p[5], location_ID = p[6], LatLong=p[7])
    cursor.execute(sql_command)



