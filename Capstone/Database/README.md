Database Conversion library
====================
This repository contains the Database Converstion library, that takes
flood data in two different formats (either csv or a JSON url) and 
inputs it into two different databases (SQLite or InfluxDB). 

The purpose of the scripts contained in this library is to organize and
format flood data collected by sensors and the GPS service Waze. The 
databases can improve accessablility, vizualization, querying, and 
analysis. 

Historical data to SQLite
----------

Data from sesnors that have previously been deployed in Norfolk, VA. and
crowd sourced data from Waze are stored in a CSV. Converting the CSV
to a retational and locally hosted database can facilitate future use cases
by allowing queries on items such as locations or types and a standardization
of the event date. 

SQLite is a locally hosted database, so only those with access to the fdata.db
can utilize it. This allowed for quick and simple construction, and rudimentary 
use cases. In the future it may be nice for the database to be hosted on the 
internet. 

Consideration for the relational database design and the enitity relationship
diagram can be found in the Database Design Pros/Cons PDF.

### dateconvert.py

This script reads the flooddata.csv and converts its current fromat to 
datetime format. This is necessary because the database needs a standardized
format for time to allow for future analysis on time series data. 
Datetime format is the most widley used for timeseries data. 

The script is only useful for the eventdate format currently probided in the 
flooddata.csv. The data provided in this csv has been used for random forest
machine learning models to predict flooding. 

Once the event date is converted to date time, it can either be exported as another 
csv or continued to be used as a Pandas python dataframe for the stacking.py script. 

### sqlTables.py

sqlTables.py uses Python's sqlite3 module to create tables in SQLite in the 
format of the ERD found in Database Design Pros/Cons PDF. 

Before running this code a blank database must be created in SQLite

### stacking.py

stacking.py reads the flooddata.csv and formats the data to fit the ERD found in 
the Database Design Pros/Cons PDF. It then inserts the data into the tables
in the SQLite database created with sqlTables.py.

To create the location table the script uses the groupby function to get 
each unique combination of latitudes and longituteds. It then creates
a dataframe with a unique identifier for each location, and blank columns
for the street and descritpion to be filled in in the future. The script 
then inserts this table into SQLite row by row. Because there are only a 
couple thousand unique locations inserting row by row is not unefficient 
in this case. 

To create the types table the script makes a list of all of the column headers,
it drops the ones that are uneeded and created a dataframe like the location
table. For each type of statistic, the script uses if statements to simultaneously
assign its type ID and description and insert it into the database. 

The values table is created using the melt function, which stacks all of the columns 
in the csv on top of each other. It then pairs each value with its type and location 
ID using the temporary latlong field which is stored in each table. The latlong field
is a string that is a combination of the latitude and longitude. The script
then inserts the data into sqlite row by row. This can take a lot of time 
if inserting many rows. 

Sensor Data to InfluxDB
----------

The second half of the project was to create a method for organizing,
storing, and visualizing live sensor data. This can be used for near
real time analysis of flooding in Norfolk. Influx is used for timeseries
data like the water level sensor data, and uses the datetime as the primary
key. It also pairs well with the visualization tool grafana. 

The Influx database is hosted on a Google Cloud virtual machine with
external IP 35.211.193.104. 

To access Influx:
- open an SSH terminal within the virtual machine
- enter "influx"
- enter "auth admin dMIST 2018" which is the username and password
- to view the databases enter "show databases"
- to use a database enter "use [data base name]"
- To view different tables enter "show measurements"
- To view the data within a table enter "select * from [measurement]"
- More documentation on influx can be found online

### water_level.py

This script must be run on the virtual machine. 

It must be uploaded in the ssh terminal then enter the command 
"python water_level.py" to run. 

For the code to run the user's virtual environement must have Python 2.7,
anaconda, and Pandas 2.19.

The script will run until terminated and updates every 6 seconds. Its output
indicates weather new data has been added to influx or not. 

How it works:

- The script takes a URL as an input that contains data in JSON format. 
- The script uses a .txt file to store the previous datetime from each time it
updates. 
- It then checks if the current datetime is different. 
- If so it parses the JSON and formats it to fit the influx table, if
not it prints "no new data available"
- If there is new data available it sets the datetime as the index
- Using the DataFrameClient Python module and the write_points function
data is writen to the influx database 
