import csv
import pandas as pd
import os
import glob

def getAllTables(fileDir):
    os.chdir(fileDir)
    sensorList = []

    for file in glob.glob('*'):
        print(file)
        fileName = file.split('.')
        sensorList.append(fileName[0])
    
    return sensorList

def createDataFrame(sensor, fileDir):
    sensorFile = "{}.csv".format(sensor)
    os.chdir(fileDir)

    df = pd.read_csv(sensorFile)
    df = df.assign(sensor_name=str(sensor))
    df = df.sort_values(by=['time'])

    return df

