from influxdb_client import InfluxDBClient
import pandas as pd
import os.path
import inspect
from datetime import datetime
import psutil
from influxdb import InfluxDBClient

# influx configuration - edit these
ifuser = "telegrafuser"
ifpass = "telegrafuser"
ifdb   = "pioggia"
ifhost = "192.168.178.48"
ifport = 8086
measurement_name = "pioggia"

filename = inspect.getframeinfo(inspect.currentframe()).filename
curr_dir = os.path.dirname(os.path.abspath(filename))

#convert csv to line protocol;
datafile= curr_dir + "/Dati/Realtime/dati_lastweek.csv"

df = pd.read_csv(datafile,sep=";", decimal=",")
df['data'] = pd.to_datetime(df['data'], format="%d/%m/%Y %H:%M")
#df["unix_time"] = df.data.astype('int64')

d=1
for d in range(len(df)):
    body = [
        {
            "measurements" : measurement_name,
            "time" : df["data"][d].to_pydatetime(),
           # "time" : df["unix_time"][d],
            "fields" : {
                    "pioggia" : df["pioggia"][d]
                }
        }
    ]

    ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)
    ifclient.write_points(body)

print("End script")
