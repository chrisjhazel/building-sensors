import mysql.connector
from mysql.connector import errorcode
import getpass
#import dBStore_msql

def getConfig(userName, pwrd, database):
    config = {
        'user': userName,
        'password': pwrd,
        'host': 'thesamiapp.cbxifsix5xv0.us-east-2.rds.amazonaws.com',
        'database': database, #This will need to change to the project specific database, leave for now
        'raise_on_warnings': True
    }

    return config

def checkDatabaseExists(userName, pwrd, databaseName):
    
    config = getConfig(userName, pwrd, databaseName)

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

mySQLuser = input("mySQL Server User: ")
mySQLpwrd = getpass.getpass("mySQL Server Password: ")
mySQLdB = input("mySQL Database: ")

mySQLDB_Exists = checkDatabaseExists(mySQLuser, mySQLpwrd, mySQLdB)
if mySQLDB_Exists:
    print("Found {} database on the remote server.".format(mySQLdB))
    #print("Start uploading data at {}.".format(uploadTime))
else:
    print("Could not find the database on the remote server")