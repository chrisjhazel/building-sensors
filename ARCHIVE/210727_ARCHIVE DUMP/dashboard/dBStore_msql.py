# This script contains a series of functions for interacting with the remote MySQL database
# Author: Chris Hazel
# Date Created: 2020.03.01
# Date Last Edit: 2020.03.22

import mysql.connector
from mysql.connector import errorcode
from keyStore import addKeys
import csv
import pandas as pd

import getpass

"""
GENERAL NOTES:

Remote server DB to have i Sensors x two tables
Sensor_data == all data
Sensor_dateInfo == tables received from local

"""
def getConfig(userName, pwrd):
    #Set the configuration for dealing with the remote server
    config = {
        'user': userName,
        'password': pwrd,
        'host': 'thesamiapp.cbxifsix5xv0.us-east-2.rds.amazonaws.com', #Add host name at time of running for a smidge more security
        'database': 'sensorDev', #This will need to change to the project specific database, leave for now
        'raise_on_warnings': True
    }

    return config

def getAllDB(userName, pwrd):
    config = getConfig(userName, pwrd)

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        sqlGetDBList = "show databases"
        cursor.execute(sqlGetDBList)

        dbList = cursor.fetchall()

        ###TEMPORARY TO RETURN DATABASE NAME
        return [config["database"]]

        
        #return dbList
    
    except Exception as e:
        print(e)
        print("Failed to receive databases")
        return 0

def getAllTables(userName, pwrd):
    config = getConfig(userName, pwrd)

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        sqlGetTableList = "show tables"
        cursor.execute(sqlGetTableList)

        tableList = cursor.fetchall()

        return tableList
    
    except Exception as e:
        print(e)
        print("Failed to receive tables")
        return 0

def checkDatabaseExists(userName, pwrd):
    #Confirm that the project database exists in the remote server
    #If the database does not exist, create one
    
    config = getConfig(userName, pwrd)

    try:
        cnx = mysql.connector.connect(**config)
        cnx.close()
        return True

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        
        cnx.close() #Likely don't need this line
        return False

def writeSensorTable(sensorName, config):
    #Create a new pair of tables, one for the data and one for the records
    columnKeys = addKeys()

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        #Create the data table
        sqlCreateTable = "CREATE TABLE {}__data (time datetime, {} float(24), {} float(24), {} float(24), {} smallint, {} smallint);".format(sensorName, columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4])
        cursor.execute(sqlCreateTable)
        cnx.commit()

        #Create the records table
        sqlCreateRecordTable = "CREATE TABLE {}__records (recordTable VARCHAR(24));".format(sensorName)
        cursor.execute(sqlCreateRecordTable)
        cnx.commit()

        return True
    
    except Exception as e:
        print(e)
        print("Could not create new tables!")
        return False

def checkTableExists(sensorName, config):
    #Confirm that sensor table exists, if table does not exist, create one
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        #Change this to read the tablesreceived table for what tables have been imported to the remote server
        sqlGetTableList = ("SHOW TABLES;")
        cursor.execute(sqlGetTableList)

        #Get the remote table list
        remoteTableList = cursor.fetchall()
        #print(remoteTableList)

        remoteTables = []
        for rTable in remoteTableList:
            remoteTables.append(rTable[0])

        #print(remoteTables)
        if (sensorName + "__data") in remoteTables:
            return True
        else:
            print("Could not find sensor table in remote database.")
            print("Attempting to create table...")

            newTable = writeSensorTable(sensorName, config)

            if newTable:
                print("New Tables created")
                return True
            else:
                print("Could not create new table")
                return False

    except Exception as e:
        print(e)
        print("Could not find or create table!")
        return False



def writeDataTable2Remote(databaseName, userName, pwrd, sensorName, dataTable, rowCounter):
    #Write the sensor data from the local server to the remote server
    columnKeys = addKeys()
    config = getConfig(userName, pwrd)

    try:
        tableExists = checkTableExists(sensorName, config)

        if tableExists:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            for dataRow in dataTable:
                tableName = sensorName + '__data'
                sqlWrite = ("INSERT INTO " + (tableName) +
                            " (time, temperature, humidity, pressure, light, sound) "
                            "VALUES (%s, %s, %s, %s, %s, %s);")
                
                sqlData = (dataRow[0], dataRow[1], dataRow[2], dataRow[3], dataRow[4], dataRow[5])
                cursor.execute(sqlWrite, sqlData)
                cnx.commit()
                rowCounter += 1
            
            return True, rowCounter
        
        else:
            print("Could not create new sensor table!")
            return False, 0
    
    except Exception as e:
        print(e)
        print("Could not record data to the remote server")
        return False

def getRemoteTableData(userName, pwrd, tableName):
    #Read the contents of a table
    config = getConfig(userName, pwrd)

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        readTable = "SELECT * FROM " + (tableName)
        cursor.execute(readTable)

        tableInfo = cursor.fetchall()

        return tableInfo
    
    except Exception as e:
        print(e)
        print("Could not read data from table!")
        return e


def createDataFrame(userName, pwrd, tableName):
    #Create a single dataframe from MySQL
    config = getConfig(userName, pwrd)

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        df = pd.read_sql_query("SELECT * FROM " + (tableName), cnx)

        df = df.assign(sensor_name=str(tableName))
        df = df.sort_values(by=['time'])

        return df

    except Exception as e:
        print(e)
        print("Could not read data from table!")
        return e
