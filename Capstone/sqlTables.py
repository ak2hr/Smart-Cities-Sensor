# Creating the tables in SQLite
import sqlite3

connection = sqlite3.connect("fdata.db", timeout=10)

cursor = connection.cursor()

#%%
## Creating SQL table
## Delete table to restart
cursor.execute("""DROP TABLE Locations;""")

sql_command1 = """
    CREATE TABLE Locations (
    location_ID INTEGER PRIMARY KEY,
    latlong VARCHAR(50),
    lat DECIMAL,
    long DECIMAL,
    street VARCHAR(50),
    description VARCHAR(50)
    );"""
cursor.execute(sql_command1)

#%%
cursor.execute("""DROP TABLE Types;""")
sql_command2 = """
    CREATE TABLE Types (
    type_ID INTEGER PRIMARY KEY,
    statistic VARCHAR(10),
    description VARCHAR(50)
    );"""
cursor.execute(sql_command2)

#%%
cursor.execute("""DROP TABLE Vals;""")

sql_command3 = """
    CREATE TABLE Vals (
    vals_ID INTEGER PRIMARY KEY,
    event_date VARCHAR(10),
    value FLOAT,
    type_ID INTEGER,
    location_ID INTEGER,
    FOREIGN KEY(type_ID) REFERENCES Types(type_ID),
    FOREIGN KEY(location_ID) REFERENCES Locations(type_ID)
    );"""
cursor.execute(sql_command3)

connection.commit()
connection.close()