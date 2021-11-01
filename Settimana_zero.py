import pandas as pd

file_to_resample = "Dati/Realtime/T0360.csv"

data = pd.read_csv(file_to_resample,sep = ";",decimal = ",")
data.Date = pd.to_datetime(data.Date,format = "%d/%m/%Y %H:%M")

new = data.rename(columns={"Date": "data", "Pioggia (mm)":"pioggia"})
new = new.set_index("data")

new = new.groupby(pd.Grouper(freq='15T')).sum()

new.index = new.index.strftime("%d/%m/%Y %H:%M")
new.to_csv("Dati/Realtime/dati_lastweek.csv", sep=";",decimal=",")