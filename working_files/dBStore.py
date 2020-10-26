# This script contains a series of functions for interacting with the PostgreSQL database
# Author: Chris Hazel
# Date Created: 2020.10.22
# Date Last Edit: 2020.10.26

"""
REFERENCES:
https://opensource.com/article/17/10/set-postgres-database-your-raspberry-pi

"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

#Set Generic user and password information to pass to each function
_user = 'sensorUser'
_password = 'sensors'
_host = 'localhost'



def testDBExists(projectName):
    # Test if the database exists
    try:
        con = psycopg2.connect(dbname='postgres', user=_user, host=_host, password=_password)
        cursor = con.cursor()

        # Get the list of database names from the PostgreSQL servers
        sqlGetDBList = ("SELECT datname FROM pg_catalog.pg_database;")
        cursor.execute(sqlGetDBList)

        dbList = cursor.fetchall()

        for item in dbList:
            # Test each name to compare to the project name, if DB exists, continue
            if item[0] == projectName:
                print("Project Database exists!")
                return True

        # If the project database does not exist, then create a new one
        return createNewProject(projectName)
    
    except Exception as e:
        print(e)
        print("Failed to check databases")
        return False


def createNewProject(projectName):
    # Create a new project database
    try:
        #Connect to Postgres Database system
        con = psycopg2.connect(dbname='postgres', user=_user, host=_host, password=_password)
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        #Set the cursor and create database command
        cursor = con.cursor()
        sqlCreateDatabase = "create database "+projectName+";"

        #Create the new project database
        cursor.execute(sqlCreateDatabase)

        return True
    
    except Exception as e:
        print(e)
        print("Failed to create new project database!")
        return False

def testTableExists(projectName, sensorTableName, columnKeys):
    # Test if the sensor table exists within the project database
    try:
        con = psycopg2.connect(dbname=projectName, user=_user, host=_host, password=_password)
        cursor = con.cursor()

        # Get the list of table names from the project database
        sqlGetTableList = ("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
        cursor.execute(sqlGetTableList)

        tableList = cursor.fetchall()

        for item in tableList:
            # Test each table name and compare to the current sensor table name
            if item[0] == sensorTableName:
                #print("Sensor Table exists!")
                return True

        # If the table does not exist, create a new table with the current name
        return createNewTable(projectName, sensorTableName, columnKeys)
    
    except Exception as e:
        print(e)
        print("Failed to check tables")
        return False

def createNewTable(projectName, sensorTableName, columnKeys):
    # Create a table
    try:
        con = psycopg2.connect(dbname=projectName, user=_user, host=_host, password=_password)
        cursor = con.cursor()

        #Create a new table with the current name
        sqlCreateTable = "create table "+sensorTableName+" (time timestamp, {} float(24), {} float(24), {} float(24), {} smallint, {} smallint);".format(columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4])
        cursor.execute(sqlCreateTable)
        con.commit()

        return True

    except Exception as e:
        print(e)
        print("Could not create new table!")
        return False

def insertDataRow(dataRow, projectName, sensorTableName, columnKeys):
    # Write the datarow to the SQL database
    try:
        con = psycopg2.connect(dbname=projectName, user=_user, host=_host, password=_password)
        cursor = con.cursor()
        con.autocommit = True

        # Write the values of the dataRow list to the SQL Table
        # Include the current date and time to the first column of the table for each row
        sqlWriteData = "INSERT INTO {} VALUES ({}, {}, {}, {}, {}, {});".format(sensorTableName, 'Now()', round(dataRow[0], 2), round(dataRow[1], 2), round(dataRow[2], 2), dataRow[3], dataRow[4])

        #print(sqlWriteData)

        # Write the data
        cursor.execute(sqlWriteData)
        con.commit

        con.close

        return True

    except Exception as e:
        print(e)
        print("Could not record data!")
        return e
