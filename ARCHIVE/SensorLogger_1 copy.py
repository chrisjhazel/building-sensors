#This script will read sensor data communicated via BLE and log the data on local storage
#Author: Chris Hazel
#Date Started: 2020.10.05
#Date Last Major Edit: 2020.10.21

"""
Notes:
This script is based off of the following script by Gary Stafford
https://programmaticponderings.com/2020/08/04/getting-started-with-bluetooth-low-energy-ble-and-generic-attribute-profile-gatt-specification-for-iot/
Reference: https://elinux.org/RPi_Bluetooth_LE

To Run in command line terminal:
python3 ./{scriptName} {MAC Address} {ProjectName} {Sensor Name}
python3 ./SensorLogger.py ed:d6:f1:0a:f7:19 Project1 Sensor1

"""

import sys
import time
import datetime
from argparse import ArgumentParser
from bluepy import btle  # linux only (no mac)
from colr import color as colr
import csv
import dBStore
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def main():
    # get args
    args = get_args()

    #Set connection count to test connection to sensor device explicit number of times
    connectCount = 0

    #Attempt to connect to BLE device and run the logger script
    while connectCount < 2:
        try:
            # Connect the sensor device to the hub
            print("Connecting…")
            nano_sense = btle.Peripheral(args.mac_address)

            # Discover the service available on the device
            print("Discovering Services…")
            _ = nano_sense.services
            environmental_sensing_service = nano_sense.getServiceByUUID("181A")

            # Discover the characteristics available on the device
            print("Discovering Characteristics…")
            _ = environmental_sensing_service.getCharacteristics()

            # Get the update frequency from the sensor and use as the update time on the hub
            updateTime = read_updateTime(environmental_sensing_service)

            #Get names for the project and the sensor
            projectName = args.project_name
            sensorName = args.sensor_name

            # Add key values as a csv file to later read
            columnKeys = addKeys(projectName)

            #If successful connection, reset connect counter to 0
            connectCount = 0

            # Test if the project database exists, if not, create new one
            dbExists = dBStore.testDBExists(projectName)

            if dbExists == True:

                #Run the data logging script
                getSensorData(environmental_sensing_service, projectName, sensorName, updateTime, columnKeys)
        
        except:
            #If not able to connect to the BLE device
            print("*****************************")
            print("COULD NOT CONNECT TO DEVICE!")
            print("----------RETRYING----------")
            print("*****************************")

            #Add to the connect counter and delay next attempt by 10 seconds
            connectCount += 1
            time.sleep(10)

            

    """
    Temporary lines for file creation on local disk

    test if database for project has been created:
        if no, create database for the project
        if yes, continue
    test if table has been created for the sensor
        if no, create the table
        if yes, continue
    write new row of data to the current sensor table

    """

    
def getSensorData(environmental_sensing_service, projectName, sensorName, updateTime, columnKeys):

    today = None
    tableExists = False

    while True:

        # Create a new CSV file on the local drive to record the data
        # Add the date to the file for some organization
        todayNow = datetime.datetime.now()

        if todayNow != today:
            today = todayNow
            csvFile = ("{}_{}__{}{}{}".format(projectName, sensorName, today.year, today.month, today.day))
            sensorTableName = ("{}__{}{}{}".format(sensorName, today.year, today.month, today.day))

            #Make a new table for today
            tableExists = dBStore.testTableExists(projectName, sensorTableName, columnKeys)

        if tableExists == True:

            # Create a datarow to collect information from each sensor characteristic
            print("\n")
            # Start the data row with the python time
            # May not need this depending on how information is being sent to the cloud db
            #dataRow = [time.time()] Use this to start the list with the python time
            dataRow = []
            dataRow.append(read_temperature(environmental_sensing_service))
            dataRow.append(read_humidity(environmental_sensing_service))
            dataRow.append(read_pressure(environmental_sensing_service))
            dataRow.append(read_light(environmental_sensing_service))
            dataRow.append(read_sound(environmental_sensing_service))

            """
            # Write the data row to a local CSV file
            with open(csvFile, "a") as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerow(dataRow)
                """
            
            dataInsertSuccess = dBStore.insertDataRow(dataRow, projectName, sensorTableName, columnKeys)
            print(dataInsertSuccess)

            time.sleep(updateTime)  # transmission frequency set on IoT device
        else:
            break


def addKeys(projectName):
    # Add the keys to a CSV file for reading later
    """
    Keys with the time component, not used in SQL
    keys = [["TIME", "TICKS"],
            ["TEMPERATURE", "°F"],
            ["HUMIDITY", "%"], 
            ["PRESSURE", "kPa"],
            ["LIGHT", "UNITS"],
            ["SOUND", "UNITS"]]
            """
    
    keys = [["TEMPERATURE", "°F"],
            ["HUMIDITY", "%"], 
            ["PRESSURE", "kPa"],
            ["LIGHT", "UNITS"],
            ["SOUND", "UNITS"]]

    #Create column key list to pass to SQL table
    columnKeys = []
    for key in keys:
        columnKeys.append(key[0])
    
    keyFile = ("{}__keys.csv".format(projectName))

    with open(keyFile, "w") as f:
        for key in keys:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(key)
    
    return columnKeys


def byte_array_to_int(value):
    # Raw data is hexstring of int values, as a series of bytes, in little endian byte order
    # values are converted from bytes -> bytearray -> int
    # e.g., b'\xb8\x08\x00\x00' -> bytearray(b'\xb8\x08\x00\x00') -> 2232

    # print(f"{sys._getframe().f_code.co_name}: {value}")

    value = bytearray(value)
    value = int.from_bytes(value, byteorder="little")
    return value


def split_color_str_to_array(value):
    # e.g., b'2660,2059,1787,4097\x00' -> 2660,2059,1787,4097 ->
    #       [2660, 2059, 1787, 4097] -> 166.0,128.0,111.0,255.0

    # print(f"{sys._getframe().f_code.co_name}: {value}")

    # remove extra bit on end ('\x00')
    value = value[0:-1]

    # split r, g, b, a values into array of 16-bit ints
    values = list(map(int, value.split(",")))

    # convert from 16-bit ints (2^16 or 0-65535) to 8-bit ints (2^8 or 0-255)
    # values[:] = [int(v) % 256 for v in values]

    # actual sensor is reading values are from 0 – 4097
    print(f"12-bit Color values (r,g,b,a): {values}")

    values[:] = [round(int(v) / (4097 / 255), 0) for v in values]

    return values


def byte_array_to_char(value):
    # e.g., b'2660,2058,1787,4097\x00' -> 2659,2058,1785,4097
    value = value.decode("utf-8")
    return value


def decimal_exponent_two(value):
    # e.g., 2350 -> 23.5
    return value / 100


def decimal_exponent_one(value):
    # e.g., 988343 -> 98834.3
    return value / 10


def decimal_exponent_three(value):
    # 1 Kilopascal (kPa) is equal to 1000 pascals (Pa)
    # to convert kPa to pascal, multiply the kPa value by 1000
    # 98834.3 -> 98.8343
    return value / 1000


def celsius_to_fahrenheit(value):
    return (value * 1.8) + 32


def read_pressure(service):
    pressure_char = service.getCharacteristics("2A6D")[0]
    pressure = pressure_char.read()
    pressure = byte_array_to_int(pressure)
    pressure = decimal_exponent_one(pressure)
    pressure = decimal_exponent_three(pressure)
    print(f"Barometric Pressure: {round(pressure, 2)} kPa")
    
    return pressure


def read_humidity(service):
    humidity_char = service.getCharacteristics("2A6F")[0]
    humidity = humidity_char.read()
    humidity = byte_array_to_int(humidity)
    humidity = decimal_exponent_two(humidity)
    print(f"Humidity: {round(humidity, 2)}%")

    return humidity


def read_temperature(service):
    temperature_char = service.getCharacteristics("2A6E")[0]
    temperature = temperature_char.read()
    temperature = byte_array_to_int(temperature)
    temperature = decimal_exponent_two(temperature)
    temperature = celsius_to_fahrenheit(temperature)
    print(f"Temperature: {round(temperature, 2)}°F")

    return temperature


def read_updateTime(service):
    update_char = service.getCharacteristics("2A6B")[0]
    update = update_char.read()
    update = byte_array_to_int(update)
    update = decimal_exponent_three(update)
    return(update)


def read_light(service):
    light_char = service.getCharacteristics(
        "adb5976d-f756-43ca-8a32-1a6cdf97601f")[0]
    light = light_char.read()
    light = byte_array_to_int(light)
    print(f"Light: {light} Units")

    return light


def read_sound(service):
    sound_char = service.getCharacteristics(
        "fbfebdd5-f415-43c9-b5d5-c3094f2c86be")[0]
    sound = sound_char.read()
    sound = byte_array_to_int(sound)
    print(f"Sound: {sound} Units")

    return sound


def get_args():
    # Get arguments passed through the command line terminal
    arg_parser = ArgumentParser(description="BLE IoT Sensor Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('project_name', help="The name of the project")
    arg_parser.add_argument('sensor_name', help="The name of the individual sensor")
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    
    main()
