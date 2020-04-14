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
keyMatrix = [["Data Type", "Value Type"], ["TIME", "S"]]
recordKeys = True

while True: #overall while loop to continuously read the data
    
    if count == 20:
        break #Just a test break to test the script

    count += 1

    ser_bytes = ser.readline() #Read the serial input data per line

    if len(ser_bytes) > 2: #Each line has two hidden characters, this reads for the blank line between readings
        lineCount = 0 #Read for the character length of each reading
        for char in str(ser_bytes): #Read each character of the line, once ':' is read, break
            if char == ":": #Read seperator between value and value type
                rowList.append(float(ser_bytes[0:(lineCount-2)].decode("utf-8")))
                if recordKeys == False:
                    break
                else:
                    prevCount = lineCount-1
            elif char == "-":
                keyRow = [str(ser_bytes[prevCount:(lineCount-1)].decode("utf-8")), str(ser_bytes[lineCount:(len(ser_bytes)-2)].decode("utf-8"))]
                keyMatrix.append(keyRow)
                break
            else:
                lineCount += 1

    else:
        with open(csvFile, "a") as f: #Write the data to the CSV file
            writer = csv.writer(f, delimiter=",")
            writer.writerow(rowList)
                
        rowList = [time.time()] #Start new liast after writing to CSV

        if recordKeys == True:
            print(keyMatrix)
            with open(keyFile, "w") as f: #Write the key data to a new file
                for row in keyMatrix:
                    writer = csv.writer(f, delimiter=",")
                    writer.writerow(row)
            recordKeys = False