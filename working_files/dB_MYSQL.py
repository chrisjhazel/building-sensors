#This script will interact with the mySQL database
#This script is intended to run sepearetly from the SensorLogger.py script and will connect all tables running in the program to the remote database
#Author: Chris Hazel
#Date Started: 2020.02.23


import mysql.connector
import psycopg2

import dBStore

def main():
    #Get arguments passed through the terminal
    args = get_args()

    #Retrieve database name from terminal when calling the script
    #Get the lower of the name to ensure it matches the database name in Postgres
    databaseName = args.database_name.lower()

    #Confirm the database exists on local
    dBExists = dBStore.testDBExists(databaseName, createNew=False)
    if dBExists != True:
        print("Database does not exist; check the database name")
        return 0
#Check for database on remote with same name

#Each day at specirfic time (6am):
#Check tables on local || Tables are named SensorName_YearMonthDay
#Check for yesterday's table(s); if tables do not exist in remote DB, add tables
#If table(s) on remote is greater than 30 days old, delete table(s)

#Go to sleep until next day at 6am

def get_args():
    # Get arguments passed through the terminal
    arg_parser = ArgumentParser(description="Database Manager")
    arg_parser.add_argument('database_name', help="Name of the project database")

    args = arg_parser.parse_args()
    return args

if __name__ == "__main__":
    main()