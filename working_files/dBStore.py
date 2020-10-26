import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

_user = 'sensorUser'
_password = 'sensors'

_host = 'localhost'



def testDBExists(projectName):
    try:
        con = psycopg2.connect(dbname='postgres', user=_user, host=_host, password=_password)
        cursor = con.cursor()

        sqlGetDBList = ("SELECT datname FROM pg_catalog.pg_database;")
        cursor.execute(sqlGetDBList)

        dbList = cursor.fetchall()

        for item in dbList:

            if item[0] == projectName:
                print("Project Database exists!")
                return True

        return createNewProject(projectName)
    
    except Exception as e:
        print(e)
        print("Failed to check databases")
        return False


def createNewProject(projectName):
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
    try:
        con = psycopg2.connect(dbname=projectName, user=_user, host=_host, password=_password)
        cursor = con.cursor()

        sqlGetTableList = ("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")
        cursor.execute(sqlGetTableList)

        tableList = cursor.fetchall()

        for item in tableList:


            if item[0] == sensorTableName:
                #print("Sensor Table exists!")
                return True

        return createNewTable(projectName, sensorTableName, columnKeys)
    
    except Exception as e:
        print(e)
        print("Failed to check tables")
        return False

def createNewTable(projectName, sensorTableName, columnKeys):
    try:
        con = psycopg2.connect(dbname=projectName, user=_user, host=_host, password=_password)
        cursor = con.cursor()
        sqlCreateTable = "create table "+sensorTableName+" (time timestamp, {} float(24), {} float(24), {} float(24), {} smallint, {} smallint);".format(columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4])
        cursor.execute(sqlCreateTable)
        con.commit()
        return True
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)

        print("Could not create new table!")
        return False

def insertDataRow(dataRow, projectName, sensorTableName, columnKeys):
    try:
        con = psycopg2.connect(dbname=projectName, user=_user, host=_host, password=_password)
        cursor = con.cursor()
        con.autocommit = True

        #sqlWriteData = "insert into {}({}, {}, {}, {}, {}) values ({}, {}, {}, {}, {});".format(sensorTableName, columnKeys[0], columnKeys[1], columnKeys[2], columnKeys[3], columnKeys[4], dataRow[0], dataRow[1], dataRow[2], dataRow[3], dataRow[4])
        sqlWriteData = "INSERT INTO {} VALUES ({}, {}, {}, {}, {}, {});".format(sensorTableName, 'Now()', round(dataRow[0], 2), round(dataRow[1], 2), round(dataRow[2], 2), dataRow[3], dataRow[4])



        print(sqlWriteData)

        cursor.execute(sqlWriteData)
        con.commit

        con.close

        return True

    except Exception as e:
        print(e)
        print("Could not record data!")
        return e