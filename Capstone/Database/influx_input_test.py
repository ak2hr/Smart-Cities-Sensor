"""
If influx is not installed in python, open anaconda command prompt and enter
'pip install influxdb'
"""

import pandas as pd
import requests
from influxdb import DataFrameClient
from influxdb import InfluxDBClient
import json
from datetime import datetime
#from apscheduler.schedulers.blocking import BlockingScheduler

#must be run using the virtual influx machine
host = 'localhost'
port = 8086
user = 'admin'
password = 'dMIST2018'
dbname = 'testfd'
protocol = 'json'

client = InfluxDBClient(host, port, user, password)
client.create_database('testfd2')
print("created")


