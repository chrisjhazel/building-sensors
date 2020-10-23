import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def createNewProject(projectName):
    try:
        #Connect to Postgres Database system
        con = psycopg2.connect(dbname='postgres', user='sensorUser', host='localhost', password='sensors')
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        #Set the cursor and create database command
        cursor = con.cursor()
        sqlCreateDatabase = "create database "+projectName+";"

        #Create the new project database
        cursor.execute(sqlCreateDatabase)

        return True
    
    except:
        print("Failed to create new project database!")
        return False

def createNewTable(projectName, sensorTableName, columnKeys):
    con = psycopg2.connect(dbname=projectName, user='sensorUser', host='localhost', password='sensors')
    cursor = con.cursor()
    sqlCreateTable = "create table "+sensorTableName+" (time datetimeoffset(0), {} float(24), {} float(24), {} float(24), {} smallint, {} smallint);".format(columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4])
    cursor.execute(sqlCreateTable)
    con.commit()

def insertDataRow(dataRow, projectName, sensorTableName):
    con = psycopg2.connect(dbname=projectName, user='sensorUser', host='localhost', password='sensors')
    cursor = con.cursor()

    sqlWriteData = "insert into {} values ({}, {}, {}, {}, {}, {});".format(sensorTableName, now(), dataRow[0], dataRow[1], dataRow[2], dataRow[3], dataRow[4])

    cursor.execute(sqlWriteData)
    con.commit