import serial
import time
import csv

ser = serial.Serial('/dev/tty.usbmodem14101')
ser.flushInput()
count = 0
rowList = [time.time()] #create a list to hold each item of data

while True: #overall while loop to continuously read the data
    
    if count == 20:
        break #Just a test break to test the script

    count += 1

    ser_bytes = ser.readline()

    if len(ser_bytes) > 2:
        rowList.append(float(ser_bytes[0:len(ser_bytes)-2].decode("utf-8")))
    else:
        with open("test_data.csv", "a") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(rowList)
                
        rowList = [time.time()]