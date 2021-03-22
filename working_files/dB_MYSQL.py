#This script will interact with the mySQL database
#This script is intended to run sepearetly from the SensorLogger.py script and will connect all tables running in the program to the remote database
#Author: Chris Hazel
#Date Started: 2020.02.23

"""
GENERAL NOTES:

Remote server DB to have i Sensors x two tables
Sensor_table1 == all data
Sensor_table2 == tables received from local

This script is a Chris OG Original

To Run in command line terminal:
python3 ./{scriptName} {ProjectName} 
python3 ./dB_MYSQL.py Project1

"""


import mysql.connector
from mysql.connector import errorcode
import psycopg2
import time
import datetime
import getpass
from argparse import ArgumentParser
import csv
import os

import dBStore
import dBStore_msql
 
################
#Set upload time
################
uploadHour = 6 #time is in 24 hour format

if uploadHour < 12:
    print("Upload time set for {} AM".format(uploadHour))
    uploadTime = "{} AM".format(uploadHour)
elif uploadHour > 12:
    print("Upload time set for {} PM".format(uploadHour-12))
    uploadTime = "{} PM".format(uploadHour-12)


def getTime(uploadHour):
    #Check the time difference between the current time and the next upload time to return the sleep time
    currentTime = datetime.datetime.now()
    tomorrowTime = currentTime + datetime.timedelta(days=1)
    tomorrowTime = tomorrowTime.replace(hour=uploadHour, minute=0, second=0)

    timeDifference = tomorrowTime - currentTime
    return timeDifference.total_seconds()

def getSensorName(tables):
    sensorName = []
    dateInfo = []

    for table in tables:
        splitName = table[0].split("__")
        if splitName[0] not in sensorName:
            sensorName.append(splitName[0])
        dateInfo.append(splitName[1])

    return sensorName, dateInfo

def getToday():
    #Get today and return string formatted to be similar to sensor table name
    today = datetime.datetime.now()
    nameStr = "__{}{}{}".format(today.year, today.month, today.day)
    return nameStr

def tableDateRef():
    #Get the formatted date for the past 30 days to delete old tables
    today = datetime.datetime.now()
    dateList = []
    counter = 0
    for i in range(30):
        todayAdj = today + datetime.timedelta(days=-counter)
        dateStr = "{}{}{}".format(todayAdj.year, todayAdj.month, todayAdj.day)
        dateList.append(dateStr)
    return dateList
"""
def checkmSQLTables(databaseName, cursor):
    #Check the mySQL tables to compare against the PostGres Tables

    #Change this to read the tablesreceived table for what tables have been imported to the remote server
    sqlGetTableList = ("SELECT table_name FROM information_scheme.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
    cursor.execute(sqlGetTableList)

    #Get the remote table list
    remoteTableList = cursor.fetchall()

    # Get the local table list
    localTableList = dBStore.getTableList(databaseName)

    tranferTables = []
    for table in localTableList:
        if table not in remoteTableList:
            tranferTables.append(table)
    
    return tranferTables
"""

"""
def transferTable2mSQL(tranferTable, cursor):
    #Add new local tables to the remote server

    #Read the table contents from the local Postgres table
    #Change this to direct to Postgres Table rather than MySQL table
    readTable = "SELECT * FROM {}".format(transferTable)
    cursor.execute(readTable)

    #Write the table to a temporary CSV file
    with open("xfer.csv", "w", newline='') as csvWriter:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description]) # write headers
        csv_writer.writerows(cursor)
    
    sensorName, dateInfo = getSensorName(transferTable)


    ### Test if table exists in database
    ### Append data to table
    ### Add Postgres table name +date to table list table on remote server
    ### Delete CSV file
"""


def main():
    #Get arguments passed through the terminal
    args = get_args()

    #Retrieve database name from terminal when calling the script
    #Get the lower of the name to ensure it matches the database name in Postgres
    databaseName = args.database_name.lower()

    #Confirm the database exists on local
    dBExists = dBStore.testDBExists(databaseName, createNew=False)
    if dBExists:
        print("Found {} database on the local disk.".format(databaseName))
        print("Now checking the remote server....")        
    else:
        print("Database does not exist; check the database name")
        return 0

    #Check for database on remote with same name
    mySQLuser = input("mySQL Server User: ")
    mySQLpwrd = getpass.getpass("mySQL Server Password: ")
    #mySQLProject = input("Project name: ")

    mySQLDB_Exists = dBStore_msql.checkDatabaseExists(mySQLuser, mySQLpwrd)
    if mySQLDB_Exists:
        print("Found {} database on the remote server.".format(databaseName))
        print("Start uploading data at {}.".format(uploadTime))
    else:
        print("Could not find the database on the remote server")
        return 0
    
    #Each day at specific time (6am):
    # Sleep until upload time
    ####
    ####
    #waitTime = getTime(uploadHour)
    #time.sleep(waitTime)
    ####
    ####
    
    connectCount = 0

    while connectCount < 1: #Change to 10
        try:
            #Get local table list to compare against remote table list
            localTableList = dBStore.getTableList(databaseName)

            #Get today to remove today's table from list
            todayStr = getToday()

            #Remove archive tables from the list
            #Archive tables have already been added to the remote table
            """
            #moved to sensor for loop to get only sensor specific tables
            for table in localTableList:
                if "__ARCHIVE" in table or todayStr in table:
                    localTableList.Remove(table)
            """

            

            #Get each sensor that is being recorded
            #print(localTableList)
            sensorNameList, dateInfoList = getSensorName(localTableList)
            print('local table list: ', localTableList)
            for sensor in sensorNameList:

                ####
                ##All data is being written to the tables
                ## Need to check table names
                ## Make sure ARCHIVE tables are not being written to the remote server
                ####
                sensorTableList = []
                for table in localTableList:
                    if str(sensor) in table[0]:
                        if "__archive" not in table[0].lower() and todayStr not in table[0]:
                            print("sensor Table: ", table[0])
                            sensorTableList.append(table[0])
                            print("today dat: ", todayStr)
                            if todayStr in table[0]:
                                print('coolio')


                print("Sensor Table List: ", sensorTableList)
                #Get remote table list to compare against local table list
                #Probably don't need this right now
                #remoteTableList = dBStore_msql.getTableList(databaseName, mySQLuser, mySQLpwrd, sensor)
                """


                for writeTable in sensorTableList:
                    dataTable = dBStore.writeTableData2CSV(databaseName, writeTable)
                    writeRemote = dBStore_msql.writeDataTable2Remote(databaseName, mySQLuser, mySQLpwrd, sensor, dataTable)
                    #writeRemote = dBStore_msql.writeCSV2Table(databaseName, mySQLuser, mySQLpwrd, sensor, csvFile)
                    #os.remove(csvFile) #Delete the csv file
                    if writeRemote:
                        tableRename = dBStore.renameTable(databaseName, writeTable)
                    else:
                        print("Could not write to remote server.")
                        print("Table name to remain.")



                """
            print("ALL DONE")
            dateCompare = tableDateRef()
            dropTables = []  
            for table in localTableList:
                #print(table)
                if "__archive" in table[0].lower():
                    splitName = table[0].split("__")
                    if splitName[1] not in dateCompare:
                        dropTables.append(table[0])

            for table in dropTables:
                dropTable = dBStore.dropTables(databaseName, table)
            
            # Sleep until upload time
            ####
            ####
            connectCount = 10 #Change to 0
            #waitTime = getTime(uploadHour)
            #time.sleep(waitTime)
            ####
            ####
        
        except Exception as e:
            print(e)
            print("Could not transfer data table to remote server!")
            
            connectCount += 1
            time.sleep(60)
         

def get_args():
    # Get arguments passed through the terminal
    arg_parser = ArgumentParser(description="Database Manager")
    arg_parser.add_argument('database_name', help="Name of the project database")

    args = arg_parser.parse_args()
    return args

if __name__ == "__main__":
    main()