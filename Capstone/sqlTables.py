# Creating the tables in SQLite
import sqlite3

connection = sqlite3.connect("fdata.db", timeout=10)

cursor = connection.cursor()

#%%
## Creating SQL table
## Delete table to restart
cursor.execute("""DROP TABLE Vals;""")

sql_command1 = """
    CREATE TABLE Vals (
    event_date VARCHAR(10),
    value FLOAT,
    type_ID VARCHAR(10),
    location_ID VARCHAR(50)
    );"""
cursor.execute(sql_command1)

#%%
cursor.execute("""DROP TABLE Locations;""")

sql_command2 = """
    CREATE TABLE Locations (
    location_ID VARCHAR(50) PRIMARY KEY,
    lat DECIMAL,
    long DECIMAL,
    street VARCHAR(50),
    description VARCHAR(50)
    );"""
cursor.execute(sql_command2)

#%%
cursor.execute("""DROP TABLE Types;""")
sql_command3 = """
    CREATE TABLE Types (
    type_ID VARCHAR(10) PRIMARY KEY,
    statistic VARCHAR(10),
    description VARCHAR(50)
    );"""
cursor.execute(sql_command3)

connection.commit()
connection.close()