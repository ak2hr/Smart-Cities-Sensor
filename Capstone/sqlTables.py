# Creating the tables in SQLite
import sqlite3

connection = sqlite3.connect("fdata.db", timeout=10)

cursor = connection.cursor()

## Delete table to restart
#cursor.execute("""DROP TABLE fevent;""")
cursor.execute("""DROP TABLE value;""")
cursor.execute("""DROP TABLE locations;""")
cursor.execute("""DROP TABLE types;""")

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
# event_date --> date time
cursor.execute(sql_command)

sql_command1 = """
    CREATE TABLE value (
    Value_ID INTEGER PRIMARY KEY,
    event_date VARCHAR(10),
    value FLOAT,
    LatLong VARCHAR(50),
    Location_ID VARCHAR(10),
    Type_ID VARCHAR(10));"""
cursor.execute(sql_command1)

sql_command2 = """
    CREATE TABLE locations (
    Location_ID INTEGER PRIMARY KEY,
    Lat DECIMAL,
    Long DECIMAL,
    LatLong VARCHAR(50),
    Street VARCHAR(50),
    Description VARCHAR(50));"""
cursor.execute(sql_command2)

sql_command3 = """
    CREATE TABLE types (
    Types_ID INTEGER PRIMARY KEY,
    Description VARCHAR(50),
    Statistic VARCHAR(10));"""
cursor.execute(sql_command3)

connection.commit()
connection.close()