"""
This script pulls current tide level data from the NOAA API using the url shown. The values are extracted from the JSON
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

    url = "https://tidesandcurrents.noaa.gov/api/datagetter?date=latest&station=8638610&product=water_level&datum=NAVD&units=english&time_zone=lst_ldt&format=json"
    response = requests.get(url)
    result = json.loads(response.text)

    station_id = str(result['metadata']['id'])
    station_name = str(result['metadata']['name'])
    lat = str(result['metadata']['lat'])
    lon = str(result['metadata']['lon'])
    value = float(result['data'][0]['v'])
    date_time_str = str(result['data'][0]['t'])
    date_time = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')

    current_date_time = str(date_time)

    if current_date_time not in previous_date_time:
        cols = ['station_id','station_name','latitude','longitude','date_time','value']
        line = pd.DataFrame({'station_id': station_id,'station_name': station_name,'latitude': lat,
                             'longitude': lon,'date_time': date_time,'value': value}, columns=cols, index=[0])


        line['date_time'] = pd.to_datetime(line['date_time'])
        line = line.set_index('date_time')
        # print line

        time_values = line[['value']]
        # print time_values

        tags = {'station_id': line[['station_id']], 'station_name': line[['station_name']],'latitude': line[['latitude']],
                'longitude': line[['longitude']]}

        client = DataFrameClient(host, port, user, password, dbname)

        # Write DataFrame with Tags
        client.write_points(line, dbname, protocol=protocol)  # , tags

        client.close()

        f = open('last_data_retrieved.txt', 'w')
        f.write(current_date_time + '\n')
        f.close()
        print "New data has been added to the database!"
    else:
        print "No new data available"


host = 'localhost'
port = 8086
user = 'admin'
password = 'dMIST2018'
dbname = 'test'
protocol = 'json'


def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(get_tide_data, 'interval', minutes=6)
    scheduler.start()
    # get_tide_data()

if __name__ == "__main__":
    main()
pull_tide_a
