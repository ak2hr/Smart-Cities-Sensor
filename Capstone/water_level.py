"""
This script pulls current tide level data from the NOAA API using the url shown. The values are extracted from the $
file and put in a dataframe. The data is then appended to the Influx database table with the connection and cursor.
"""
import pandas as pd
import requests
from influxdb import DataFrameClient
import json
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

def get_tide_data():
    with open("last_data_retrieved.txt") as f:
        previous_date_time = f.readlines()
        
    url = "https://gentle-falls-78142.herokuapp.com/"
    response = requests.get(url)
    result = json.loads(response.text)
    
    sensor_id = str(result['metadata']['id'])
    sensor_name = str(result['metadata']['name'])
    lat = str(result['metadata']['lat'])
    lon = str(result['metadata']['lon'])
    flood = str(result['data'][0]['f'])
    value = float(result['data'][0]['v'])
    date_time_str = str(result['data'][0]['t'])
    
    date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
    current_date_time = str(date_time)
    
    if current_date_time not in previous_date_time:
        cols = ['sensor_id','sensor_name','latitude','longitude', 'flood', 'date_time','value']
        line = pd.DataFrame({'sensor_id': sensor_id,'sensor_name': sensor_name,'latitude': lat,
                             'longitude': lon,'flood': flood,'date_time': date_time,'value': value}, columns=cols, index=[0])
    
        line['date_time'] = pd.to_datetime(line['date_time'])
        
        line = line.set_index('date_time')
        # print line
        
        time_values = line[['value']]
        print(time_values)
        
        tags = {'sensor_id': line[['sensor_id']], 'sensor_name': line[['sensor_name']],'latitude': line[['latitude']],
                'longitude': line[['longitude']], 'flood': line[['flood']]}
    
        client = DataFrameClient(host, port, user, password, dbname)
        # Write DataFrame with Tags
        
        client.write_points(line, dbname, protocol=protocol)  # , tags
        client.close()

        f = open('last_data_retrieved.txt', 'w')
        f.write(current_date_time) # + '\n')
        f.close()
        print "New data has been added to the database!"
    else:
        print "No new data available"
    
host = 'localhost'
port = 8086
user = 'admin'
password = 'dMIST2018'
dbname = 'water_level'
protocol = 'json'

def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(get_tide_data, 'interval', minutes=0.1)
    scheduler.start()
    # get_tide_data()
    
if __name__ == "__main__":
    main()