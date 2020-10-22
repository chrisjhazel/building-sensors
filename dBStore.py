import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

con = psycopg2.connect(dbname='postgres', user='sensorUser', host='localhost', password='sensors')
con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cursor = con.cursor()
name_Database = "ProjectName"

sqlCreateDatabase = "create database "+name_Database+";"

cursor.execute(sqlCreateDatabase)