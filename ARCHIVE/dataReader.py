import serial
import time
import csv

fileName = "test_data_2"
csvFile = ("{}.csv".format(fileName))
keyFile = ("{}_keys.csv".format(fileName))

def keyReader(keyFile):
    #Read the CSV key file to determine the data types and values used
    #dataDict = {}
    dataType = []
    valueType = []

    with open(keyFile, newline = '') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i != 0:
                dataType.append(row[0])
                valueType.append(row[1])
            else:
                continue
    return dataType, valueType


def timeReader(csvFile, timeInd):
    with open(csvFile, newline = '') as f:
        reader = csv.reader(f)
        for row in reader:
            realTime = time.asctime(time.localtime(float(row[timeInd])))
            print(realTime)


dataType, valueType = keyReader(keyFile)
timeInd = dataType.index("TIME")
timeReader(csvFile, timeInd)