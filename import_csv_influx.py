from influxdb import InfluxDBClient
import uuid
import random
import time
import pandas as pd
import os.path
import inspect
from datetime import datetime
import psutil
from influxdb import InfluxDBClient

filename = inspect.getframeinfo(inspect.currentframe()).filename
curr_dir = os.path.dirname(os.path.abspath(filename))

#convert csv to line protocol;
datafile= curr_dir + "/Dati/Realtime/dati_lastweek.csv"

df = pd.read_csv(datafile,sep=";", decimal=",")
df['data'] = pd.to_datetime(df['data'], format="%d/%m/%Y %H:%M")
df["unix_time"] = df.data.astype('int64')

#client = InfluxDBClient(host='localhost', port=8086)
client = InfluxDBClient(host='192.168.178.48', port=8086)
client.create_database('writetest')

measurement_name = 'pioggia'

data = []

for i in range(len(df)):
    data.append("{measurement},value={value},i {timestamp}"
                .format(measurement=measurement_name,
                        value=df.pioggia[i],
                        timestamp=df.unix_time[i]))

client.write_points(data, database='writetest', time_precision='n', batch_size=10000, protocol='line')

