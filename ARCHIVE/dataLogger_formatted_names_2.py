import socket
from multiprocessing import process
import dropbox
import requests
import serial
import time
import csv

fileName = "test_data_2"
csvFile = ("{}.csv".format(fileName))
keyFile = ("{}_keys.csv".format(fileName))

ser = serial.Serial('/dev/tty.usbmodem14101')
ser.flushInput()
count = 0
rowList = [time.time()] #create a list to hold each item of data

#Read the first data input for the value keys
keyMatrix = [["Data Type", "Value Type"], ["TIME", "ticks"]]
recordKeys = True

#Dropbox App Information
appKey = "6op9z97xwkn5jhj"
appSecret = "uqx1j0k7kkb2h5n"

def readData(ser_bytes):
#This function reads the serial port for the sensor data
    if len(ser_bytes) > 2:  # Each line has two hidden characters, this reads for the blank line between readings
        lineCount = 0  # Read for the character length of each reading
        for char in str(ser_bytes):  # Read each character of the line, once ':' is read, break
            if char == ":":  # Read seperator between value and value type
                rowList.append(
                    float(ser_bytes[0:(lineCount-2)].decode("utf-8")))
                if recordKeys == False:
                    break
                else:
                    prevCount = lineCount-1
            elif char == "-":
                keyRow = [str(ser_bytes[prevCount:(lineCount-1)].decode("utf-8")),
                              str(ser_bytes[lineCount:(len(ser_bytes)-2)].decode("utf-8"))]
                keyMatrix.append(keyRow)
                break
            else:
                lineCount += 1

    else:
        if recordKeys == True:
            print(keyMatrix)
            with open(keyFile, "w") as f: #Write the key data to a new file
                for row in keyMatrix:
                    writer = csv.writer(f, delimiter=",")
                    writer.writerow(row)
            recordKeys = False

        with open(csvFile, "a") as f: #Write the data to the CSV file
            writer = csv.writer(f, delimiter=",")
            writer.writerow(rowList)
                
        rowList = [time.time()] #Start new list after writing to CSV

def saveDropbox(csvFile):
    #This function will save the data to a dropbox folder
    dBfilepath = r'\sensorData'
    dropbox.dropbox.files_upload(csvFile, dBfilepath, mode=WriteMode('add', None))

while True: #overall while loop to continuously read the data

    ser_bytes = ser.readline() #Read the serial input data per line
    readData(ser_bytes)


    

    time.sleep(2) #Sleep for 2 seconds between readings


#Code to test internet connection
REMOTE_SERVER = "one.one.one.one"


def is_connected(hostname):
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(hostname)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    s.close()
    return True
  except:
     pass
  return False


%timeit is_connected(REMOTE_SERVER)
> 10 loops, best of 3: 42.2 ms per loop
