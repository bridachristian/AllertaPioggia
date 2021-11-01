from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from datetime import timedelta, datetime
from dateutil import tz
import os
import numpy as np
from bob_telegram_tools.bot import TelegramBot
import os.path

import matplotlib.pyplot as plt
import seaborn as sns

# --- Impostazioni generali ---
# Definizione url
# url = 'http://dati.meteotrentino.it/service.asmx/ultimiDatiStazione?codice=T0071'
url = 'http://dati.meteotrentino.it/service.asmx/ultimiDatiStazione?codice=T0360'

# Definizione soglie di allarme
# curr_dir = os.getcwd()

import inspect
filename = inspect.getframeinfo(inspect.currentframe()).filename
curr_dir = os.path.dirname(os.path.abspath(filename))

file_soglie = curr_dir + "/Dati/soglie_pluviometriche_passotonale.csv"
soglie = pd.read_csv(file_soglie,sep=";",decimal=",")
soglie = soglie.set_index("t_ritorno")

soglia1 = soglie[soglie.index == "tr2"]    # da verifica con dati storici tempo ritorno soglia 1  = 2 anni
soglia2 = soglie[soglie.index == "tr10"]   # da verifica con dati storici tempo ritorno soglia 2  = 10 anni

# soglia1 = 48 # dati calcolati su tonale t0360 (97,5 percentile)
# soglia2 = 61 # dati calcolati su tonale t0360 (99 percentile)

# Defizione timezone
italy_tz = tz.gettz("Europe/Rome")

# Imposto credenziali bot telegram
# nome bot: allerta_pioggia_bot
# username: @pioggia_ossana_bot
token = '1838401115:AAFOFMUBjoTvoVSmwr-OaWE3YMoLZi8s0Jg'
#user_id = int('467116928')
chat_id = int("-421636330")
#bot = TelegramBot(token, chat_id)
bot = TelegramBot(token, chat_id)

# File settimana precedente
file_weekly = curr_dir + "/Dati/Realtime/dati_lastweek.csv"

# --- Script ---
# Importazione dati recenti stazione meteo Mezzana (T0071)
# da portale OpenData Trentino https://dati.trentino.it/dataset/dati-recenti-delle-stazioni-meteo
with urlopen(url) as f:
   data = f.read()

# Parsing xml
Bs_data = BeautifulSoup(data, "xml")

# Estrazione timeseries delle Precipitazioni in un dataframe
b_unique = Bs_data.find_all('precipitazione')
df_cols = ["data", "pioggia"]
rows = []
for node in b_unique:
   #print(node)
   s_data = node.find("data").text if node is not None else None
   s_pioggia = node.find("pioggia").text if node is not None else None
   rows.append({"data": s_data, "pioggia": s_pioggia})
out_df = pd.DataFrame(rows, columns=df_cols)

out_df.data = pd.to_datetime(out_df.data)
out_df.pioggia = out_df.pioggia.astype(float)

out_df = out_df.set_index('data')

# Estrazione orario attuale e ultime 24 ore
start_script = pd.to_datetime(str(datetime.now()))
from_date = np.datetime64(start_script - timedelta(days=5, hours=1)) # finestra di 5 giorni per poter fare rolling
out_df = out_df[out_df.index >= from_date]

# Lettura e update del file settimanale
if os.path.exists(file_weekly):
   week_df = pd.read_csv(file_weekly,sep = ";",decimal = ",")
   week_df.data = pd.to_datetime(week_df.data,format = "%d/%m/%Y %H:%M")
   week_df = week_df.set_index("data")
   total_df = pd.concat([week_df[week_df.index < out_df.index[0]],out_df])
else : total_df = out_df

# Calcolo somma precipitazioni ultime 24h
total_df = total_df[total_df.index >= from_date]

# Aggiorno il file delle ultima settimana
update_week = total_df
update_week = update_week.reset_index()
update_week.to_csv(file_weekly,sep=";",decimal=",", index=False,date_format="%d/%m/%Y %H:%M")

# out_df = out_df[out_df.index >= from_date]
# out_df['cumulata'] = out_df.pioggia.cumsum()
# total_df['cumulata'] = total_df.pioggia.cumsum()
# total_df = total_df.groupby(pd.Grouper(freq='1h')).sum() # nuovo, da testare

total_df['1h'] = total_df.pioggia.rolling(4).sum()
# total_df['1h'] = total_df.pioggia
# total_df['3h'] = total_df.pioggia.rolling(6*3).sum()
total_df['3h'] = total_df.pioggia.rolling(3*4).sum()
total_df['6h'] = total_df.pioggia.rolling(6*4).sum()
total_df['12h'] = total_df.pioggia.rolling(12*4).sum()
total_df['24h'] = total_df.pioggia.rolling(24*4).sum()
total_df['48h'] = total_df.pioggia.rolling(48*4).sum()
total_df['72h'] = total_df.pioggia.rolling(72*4).sum()

# Invio messaggio telegram
file_token_soglia1 = curr_dir + "/lock_file/token_soglia1.lock"
file_token_soglia2 = curr_dir + "/lock_file/token_soglia2.lock"

# Reset dei file di alert dopo 48h dalla creazione  # da verificare
if os.path.exists(file_token_soglia1):
   t1_c = datetime.fromtimestamp(os.path.getctime(file_token_soglia1))
   if (start_script - t1_c) > timedelta(days=2) :
      os.remove(file_token_soglia1)

if os.path.exists(file_token_soglia2):
   t2_c = datetime.fromtimestamp(os.path.getctime(file_token_soglia2))
   if (start_script - t2_c) > timedelta(days=2) :
      os.remove(file_token_soglia2)

# OLD: Reset dei file di alert dopo 1 giorno senza precipitazioni
# OLD: Somma delle precipitazioni giornaliere < 1 o cumulata < soglia1  # da verificare
# !!!!!!!!!! da capire quando riattivare l'allarme
# if (total_df.pioggia.sum() < 1) | (total_df.cumulata[-1] < soglia1) :
#    if os.path.exists(file_token_soglia1):
#       os.remove(file_token_soglia1)
#    if os.path.exists(file_token_soglia2):
#       os.remove(file_token_soglia2)

alert1 = []
alert2 = []
for cn in total_df.columns[3:]: # allarme pioggia con soglie dalle 6 alle 48h
   alert1.append(total_df[cn][-1] > soglia1[cn])
   alert2.append(total_df[cn][-1] > soglia2[cn])

alert1 = pd.DataFrame(alert1).transpose()
alert2 = pd.DataFrame(alert2).transpose()

alerts = pd.concat([alert1,alert2])

# Da implementare la parte sottostante sulla base della nuova tabella 'alerts'
if (alerts.iloc[0].any()) & (os.path.exists(file_token_soglia1) == False):
   quando = alerts.iloc[0][alerts.iloc[0]].index[0]
# Invio messaggi di alert
   bot.send_image("Immagini/triangolo_giallo.png")
   messaggio = "Attenzione! Superata la prima soglia di attenzione."
   bot.send_text(messaggio)
   bot.send_text("Data e ora: " + total_df.index[-1].strftime(format = "%d-%m-%Y %H:%M")  + \
                 ". Nelle ultime " + quando +" sono caduti: " + str(total_df[quando][-1].round(1)) + 'mm')
   print("Messaggio allerta 1 inviato!")
   f1 = open(file_token_soglia1, "x")
   f1.close()

if (alerts.iloc[1].any()) & (os.path.exists(file_token_soglia2) == False) :
   quando = alerts.iloc[1][alerts.iloc[1]].index[0]
   bot.send_image("Immagini/triangolo_rosso.png")
   messaggio = "Allerta! Superata la seconda soglia di attenzione."
   bot.send_text(messaggio )
   bot.send_text("Data e ora: " + total_df.index[-1].strftime(format="%d-%m-%Y %H:%M") + \
                 ". Nelle ultime " + quando + " sono caduti: " + str(total_df[quando][-1].round(1)) + 'mm')
   print("Messaggio allerta 2 inviato!")
   f2 = open(file_token_soglia2, "x")
   f2.close()


# plot
mat = alerts.transpose()
mat = mat.astype(int)
mat["Alert"] = mat["tr2"] + mat["tr10"]
mat = mat.Alert
mat = mat[mat> 0]

var_alert = list(mat.index)

gr_data = total_df[var_alert]

# from datetime import datetime,timezone
#
# now = datetime.now(timezone.utc)
#
# current_time = now.strftime("%Y-%m-%d %H:%M:%S")
# print("Last Run:", current_time + "UTC")

import pytz
from datetime import datetime, timezone
from tzlocal import get_localzone

utc_dt = datetime.now(timezone.utc)


ROM = pytz.timezone('Europe/Rome')
current_time = utc_dt.astimezone(ROM).strftime("%Y-%m-%d %H:%M:%S")
print("--- Last Run OK: ", current_time + " ---")

last_row = total_df.tail(1).drop(columns=["pioggia","1h","3h"])
thres = soglia1.drop(columns=["1h","3h"])
df_last = last_row.append(thres)
df_last = df_last.rename(index={'tr2': 'soglia'})

df_last = df_last.round(1)
print(df_last)
print("")
# Dates = out_df.reset_index()
# Tmean = doystats['T2M_mean']
# Tmax = doystats['T2M_MAX_mean']
# Tmin = doystats['T2M_MIN_mean']
#
# ax1.plot(Dates, Tmean, 'g', Dates, Tmax, 'r', Dates, Tmin, 'k')
#
# # Make the y-axis label
# ax1.set_ylabel('Temperature (C)')
# ax1.tick_params('y')
# Creating twin axes for precipitation as a bar graph on secondary XY axes
# ax2 = ax1.twiny()
# ax3 = ax2.twinx()
#
# #data for bar graph
# doy = doystats['DOY_']
# myRain = doystats['PRECTOT_mean']
#
# ax3.bar(doy, myRain, color='b')
# ax2.set_xticks([])                # to hide ticks on the second X-axis - top of the graph
# ax3.set_ylabel('Precipitation (mm)', color='b')
# ax3.tick_params('y', colors='b')
# ax3.set_ylim(top=30)
#
# # Formatting Date X-axis with monthly scale
# months = mdates.MonthLocator()  # every month
# days = mdates.DayLocator()       # every day
# myFmt = mdates.DateFormatter('%b')
# ax1.xaxis.set_major_locator(months)
# ax1.xaxis.set_major_formatter(myFmt)
# ax1.xaxis.set_minor_locator(days)
#
# # Formatting second X-axis (DOY integers) to disappear
# ax2.xaxis.set_major_formatter(plt.NullFormatter())
#
# # Displaying grid for the Date axis
# ax1.grid(True)

