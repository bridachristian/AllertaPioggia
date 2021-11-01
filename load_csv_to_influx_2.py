#from influxdb_client import InfluxDBClient
#import pandas as pd
#import os.path
#import inspect
#import datetime
#import psutil
#from influxdb import InfluxDBClient

## influx configuration - edit these
#ifuser = "telegrafuser"
#ifpass = "telegrafuser"
#ifdb   = "telegraf"
#ifhost = "192.168.178.48"
#ifport = 8086
#measurement_name = "pioggia"
#
#filename = inspect.getframeinfo(inspect.currentframe()).filename
#curr_dir = os.path.dirname(os.path.abspath(filename))
#
##convert csv to line protocol;
#datafile= curr_dir + "/Dati/Realtime/dati_lastweek.csv"
#
#df = pd.read_csv(datafile,sep=";", decimal=",")
#df['data'] = pd.to_datetime(df['data'], format="%d/%m/%Y %H:%M")
#df["unix_time"] = df.data.astype('int64')
#df.set_index(['unix_time'])
#
#body = [
#    {
#        "measurements" : measurement_name,
#        "time" : df.unix_time,
#        "fields" : {
#                "pioggia" : df.pioggia
#            }
#    }
#]
#
#ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass, ifdb)
#
#ifclient.write_points(body)

#!/usr/bin/env python

import datetime
import psutil
from influxdb import InfluxDBClient

# influx configuration - edit these
ifuser = "telegrafuser"
ifpass = "telegrafuser"
ifdb   = "test1"
ifhost = "192.168.178.48"
ifport = 8086
measurement_name = "system"

# take a timestamp for this measurement
time = datetime.datetime.utcnow()

# collect some stats from psutil
disk = psutil.disk_usage('/')
mem = psutil.virtual_memory()
load = psutil.getloadavg()

# format the data as a single measurement for influx
body = [
    {
        "measurement": measurement_name,
        "time": time,
        "fields": {
            "load_1": load[0],
            "load_5": load[1],
            "load_15": load[2],
            "disk_percent": disk.percent,
            "disk_free": disk.free,
            "disk_used": disk.used,
            "mem_percent": mem.percent,
            "mem_free": mem.free,
            "mem_used": mem.used
        }
    }
]

# connect to influx
ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)

# write the measurement
ifclient.write_points(body)
