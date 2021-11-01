# Tomorrow.io
import requests, json
import pandas as pd

apikey = 'tfGNiIoiMpBzOPXGCjiugjKASxmxJ7Sn'
base_url ="https://api.tomorrow.io/v4/timelines?"
location = "46.2626,10.5968"   # Passo Tonale
fields="precipitationIntensity"
timesteps="1h"
units="metric"
complete_url = base_url + "location="+location + "&fields=" + fields + "&timesteps="+timesteps + "&units=" + units + "&apikey=" + apikey
response =  requests.get(complete_url)
x = response.json()

y = x["data"]
z = y["timelines"]
k = z[0]
timeline_list = k["intervals"]

df = pd.DataFrame(timeline_list)

df["values"][1].values()
i = 0
key=[]
val=[]
for i in range(len(df)):
    key_i = df["startTime"][i]
    val_i = list(df["values"][i].values())[0]
    key.append(key_i)
    val.append(val_i)

tomorrowio = val
mydf_tomor = pd.DataFrame({"timestamp":key, "tomorrowio":tomorrowio})
mydf_tomor["timestamp"] = pd.to_datetime(mydf_tomor["timestamp"], format="%Y-%m-%dT%H:%M:%SZ")

# mydf["cumsum"] = mydf.precipitation.cumsum()




# Openweather map

import requests, json
import pandas as pd
import math

apikey = '320acebea46fa43f49cd9d2153b747e1'

base_url = "https://api.openweathermap.org/data/2.5/onecall?"
lat="46.2626"
lon="10.5968"
exclude="current,minutely,daily,alerts"
appid=apikey
units="metric"

complete_url = base_url + "lat="+lat + "&lon=" + lon + "&exclude="+exclude + "&units=" + units + "&appid=" + appid

response =  requests.get(complete_url)
x = response.json()

data = x["hourly"]
df = pd.DataFrame(data)

df['dt'] = pd.to_datetime(df['dt'],unit='s')

df["fff"] = pd.isna(df['rain'])
df.rain[df['fff']==True] = dict({"1h": 0})

i = 0
key=[]
val=[]
for i in range(len(df)):
    key_i = df["dt"][i]
    # val_test = float(df["rain"][i])
    # if(pd.isna(val_test)):
    #     val_i = 0
    # else:
    val_i = list(df["rain"][i].values())[0]
    key.append(key_i)
    val.append(val_i)

openweather = val

mydf_open = pd.DataFrame({"timestamp":key, "openweather":openweather})

#join

mydf = pd.merge(mydf_tomor, mydf_open,how="outer", left_on="timestamp",right_on="timestamp")
mydf = mydf.iloc[0:49]


import seaborn as sns
import matplotlib.pyplot as plt

f, ax = plt.subplots(1, 1)

sns.lineplot(data=mydf, x="timestamp", y="tomorrowio",color = "blue", label = "tomorrowio" )
sns.lineplot(data=mydf, x="timestamp", y="openweather",color = "red",label = "openweather")

ax.legend()
