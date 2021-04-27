import pandas as pd
import mysql.connector

import dBStore_msql
from remote_connect import remote_connect

remote_access = remote_connect()

tableList = dBStore_msql.getAllTables(remote_access[0], remote_access[1])  # Remove before upload
sensorList = []
for s in tableList:
    if "data" in s[0].lower():
        sensorList.append(s[0])

for sensor in sensorList:
    df = dBStore_msql.createDataFrame(remote_access[0], remote_access[1], sensor)
    csvFile = "{}.csv".format(sensor)
    df.to_csv(csvFile)