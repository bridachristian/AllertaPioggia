rm(list = ls())
options(scipen=999)

library(dplyr,quietly = T)

getwd()
setwd(getwd())

print(paste("--- Start script: ", Sys.time(),"---"))
print(paste("Script folder:", getwd()))

# dir =  getwd() #linux dir
dir =  "/home/ubuntu/git/AllertaPioggia" #linux dir

t1 = Sys.time()
file_csv = paste(dir,"/Dati/Realtime/dati_lastweek.csv",sep="")

data = read.csv(file_csv, stringsAsFactors = F,sep = ";",dec = ",",row.names = NULL)
data$data = as.POSIXct(data$data, format = "%d/%m/%Y %H:%M", tz= "Etc/GMT-1")


data = data %>% mutate(datetime_ns = as.numeric(data)*1000000000)
line = c()

data = data %>%
  mutate(line = paste("pioggia", " value=", pioggia, " ",datetime_ns, sep=""))

line = c(data$line)

filename = paste("./Dati/Realtime/dati_lastweek.txt",sep = "")
output.file <- file(filename, "wb") 

write("# DDL", file = output.file)
write("",file = output.file, append = TRUE)
write("# DML", file = output.file, append = TRUE)
write("# CONTEXT-DATABASE: pioggia", file = output.file, append = TRUE)
write("",file = output.file, append = TRUE)
write.table(x = line, file = output.file,
            quote = FALSE,row.names = FALSE, col.names = FALSE,append = TRUE)
close(output.file)

print(paste("--- End script: ", Sys.time(),"---"))

