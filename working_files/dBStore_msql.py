import mysql.connector
from mysql.connector import errorcode
from keyStore import addKeys
import csv

import getpass

"""
GENERAL NOTES:

Remote server DB to have i Sensors x two tables
Sensor_data == all data
Sensor_dateInfo == tables received from local

"""
def getConfig(userName, pwrd):
    config = {
        'user': userName,
        'password': pwrd,
        'host':,
        'database': 'sensorDev', #This will need to change to the project specific database, leave for now
        'raise_on_warnings': True
    }

    return config



def checkDatabaseExists(userName, pwrd):
    
    config = getConfig(userName, pwrd)

    try:
        cnx = mysql.connector.connect(**config)
        #print("Found {} data on the remote server.".format(databaseName))
        # print("Start uploading data at {}.".format(uploadTime))
        
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
"""
def writeSensorTable__ARCHIVE(databaseName, userName, pwrd, sensorName):
    config = getConfig(userName, pwrd)
    columnKeys = addKeys()

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        #Create the data table
        sqlCreateTable = "CREATE TABLE {}__data (time timestamp, {} float(24), {} float(24), {} float(24), {} smallint, {} smallint);".format(sensorName, columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4])
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
"""
def writeSensorTable(sensorName, config):
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

"""
def getTableList__ARCHIVE(databaseName, userName, pwrd, sensorName):

    config = getConfig(userName, pwrd)

    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        #Change this to read the tablesreceived table for what tables have been imported to the remote server
        sqlGetTableList = ("SELECT table_name FROM information_scheme.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
        cursor.execute(sqlGetTableList)

        #Get the remote table list
        remoteTableList = cursor.fetchall()

        sensorRecordsTable = "{}__records".format(sensorName)

        if sensorRecordsTable in remoteTableList:
            getSensorDateInfo = ("SELECT * FROM {}".format(sensorRecordsTable))
            cursor.execute(getSensorDateInfo)

            sensorDateTable = cursor.fetchall()

            return sensorDateTable
        else:
            print("Could not find sensor table in remote database.")
            print("Attempting to create table...")

            newTable = writeSensorTable(databaseName, userName, pwrd, sensorName)

            if newTable:
                print("New Tables created")
                return []
            
            else:
                print("Could not create new tables!")
                return 0
    except Exception as e:
        print(e)
        print("Could not create new table!")
        return False
"""
def checkTableExists(sensorName, config):

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



def writeDataTable2Remote(databaseName, userName, pwrd, sensorName, dataTable):

    columnKeys = addKeys()
    config = getConfig(userName, pwrd)

    try:
        tableExists = checkTableExists(sensorName, config)

        if tableExists:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            for dataRow in dataTable:
                #print("dataRow", dataRow)
                #sqlWriteData = "INSERT INTO {} (TIME, {}, {}, {}, {}, {}) VALUES ({}, {}, {}, {}, {}, {});".format((sensorName + "__data"), columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4], dataRow[0], dataRow[1], dataRow[2], dataRow[3], dataRow[4], dataRow[5])
                #cursor.execute(sqlWriteData)
                tableName = sensorName + '__data'
                sqlWrite = ("INSERT INTO " + (tableName) +
                            " (time, temperature, humidity, pressure, light, sound) "
                            "VALUES (%s, %s, %s, %s, %s, %s);")
                
                sqlData = (dataRow[0], dataRow[1], dataRow[2], dataRow[3], dataRow[4], dataRow[5])
                cursor.execute(sqlWrite, sqlData)
                cnx.commit()
            
            return True
        
        else:
            print("Could not create new sensor table!")
            return False
    
    except Exception as e:
        print(e)
        print("Could not record data to the remote server")
        return False

"""
def writeDataTable2Remote__ARCHIVE(databaseName, userName, pwrd, sensorName, dataTable):

    columnKeys = addKeys()
    config = getConfig(userName, pwrd)

    try:
        tableExists = checkTableExists(sensorName, config)

        if tableExists:
            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            for dataRow in dataTable:
                print("dataRow", dataRow)
                sqlWriteData = "INSERT INTO {} (TIME, {}, {}, {}, {}, {}) VALUES ({}, {}, {}, {}, {}, {});".format((sensorName + "__data"), columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4], dataRow[0], dataRow[1], dataRow[2], dataRow[3], dataRow[4], dataRow[5])
                cursor.execute(sqlWriteData)
                cnx.commit()
            
            return True
        
        else:
            print("Could not create new sensor table!")
            return False
    
    except Exception as e:
        print(e)
        print("Could not record data to the remote server")
        return False


def writeCSV2Table(databaseName, userName, pwrd, sensorName, csvFileName):

    columnKeys = addKeys()
    config = getConfig(userName, pwrd)

    try:

        tableExists = checkTableExists(sensorName, config)

        if tableExists:

            cnx = mysql.connector.connect(**config)
            cursor = cnx.cursor()

            with open(csvFileName, "r", newline='') as csvFile:
                tableData = csv.reader(csvFile)
                #tableData = csvFile.readline()

                for dataRow in tableData:
                    print("dataRow: ", dataRow)
                    print("columnKeys: ", columnKeys)
                    sqlWriteData = "INSERT INTO {} (TIME, {}, {}, {}, {}, {}) VALUES ({}, {}, {}, {}, {}, {});".format((sensorName + "__data"), columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4], dataRow[0], dataRow[1], dataRow[2], dataRow[3], dataRow[4], dataRow[5])
                    cursor.execute(sqlWriteData)
                    cnx.commit()
            
            #Should add a snippet here to add record key
                
            return True
        
        else:
            print("Could not create new sensor table!")
            return False
    
    except Exception as e:
        print(e)
        print("Could not record data to the remote server")
        return False
"""