import pandas as pd
import os



sensorNumber = 1
fileName = "sensorDev_sensor{}__data".format(sensorNumber)
filePath = "dataDump/{}.sql".format(fileName)

# Read the sql file
query = open(filePath, 'r')

# connection == the connection to your database, in your case prob_db
DF = pd.read_sql_query(query.read())
query.close()

print(DF)