rm(list = ls())
options(scipen=999)

library(dplyr)
library(stringr)
library(influxdbr)
library(xts)


con <- influx_connection(host = "192.168.178.48",user = "telegrafuser", pass = "telegrafuser")

t1 = Sys.time()
file_csv = "./Dati/Realtime/dati_lastweek.csv"

data = read.csv(file_csv, stringsAsFactors = F,sep = ";",dec = ",",row.names = NULL)
data$data = as.POSIXct(data$data, format = "%d/%m/%Y %H:%M", tz= "Etc/GMT-1")


# data = data %>% mutate(datetime_ns = as.numeric(data)*1000000000)
# line = c()
# 
# data = data %>%
#   mutate(line = paste("pioggia", " value=", pioggia, " ",datetime_ns, sep=""))
# 
# line = c(all_new$line)


influx_write(con = con, 
             db = "piogggia",
             x = data,
             time_col = "data",
             measurement = "pioggia")