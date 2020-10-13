import sys
import time
import datetime
from argparse import ArgumentParser
from bluepy import btle  # linux only (no mac)
from colr import color as colr
import csv


# BLE IoT Sensor Demo
# Author: Gary Stafford
# Reference: https://elinux.org/RPi_Bluetooth_LE
# Requirements: python3 -m pip install –user -r requirements.txt
# To Run: python3 ./TestBLELogger.py ED:D6:F1:0A:F1:19 <- MAC address – change me!

projectName = "testData"
sensorName = "testSensor"

addKeys(projectName)

def main(projectName, sensorName):
    # get args
    args = get_args()

    print("Connecting…")
    nano_sense = btle.Peripheral(args.mac_address)

    print("Discovering Services…")
    _ = nano_sense.services
    environmental_sensing_service = nano_sense.getServiceByUUID("181A")

    print("Discovering Characteristics…")
    _ = environmental_sensing_service.getCharacteristics()

    updateTime = read_updateTime(environmental_sensing_service)

    """
    Temporary lines for file creation on local disk
    """
    today = datetime.datetime.today
    csvFile = ("{}_{}__{}{}{}.csv".format(projectName, sensorName, today.year, today.month, today.day))

    
    while True:
        """
        Create test to determine if the csv file has been pushed to the cloud DB
        If file pushed, create a new results file with the date in title

        if newFile == True:
            today = datetime.datetime.today
            csvFile = ("{}_{}__{}{}{}.csv".format(projectName, sensorName, today.year, today.month, today.day))
        """
        

        print("\n")
        dataRow = [time.time()]
        dataRow.append(read_temperature(environmental_sensing_service))
        dataRow.append(read_humidity(environmental_sensing_service))
        dataRow.append(read_pressure(environmental_sensing_service))
        dataRow.append(read_light(environmental_sensing_service))
        dataRow.append(read_sound(environmental_sensing_service))

        with open(csvFile, "a") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(dataRow)

        time.sleep(updateTime) # transmission frequency set on IoT device

def addKeys(projectName):
    keys = [["TIME", "TICKS"],
            ["TEMPERATURE", "°F"],
            ["HUMIDITY", "%"], 
            ["PRESSURE", "kPa"],
            ["LIGHT", "UNITS"],
            ["SOUND", "UNITS"]]
    
    keyFile = ("{}__keys.csv".format(projectName))

    with open(keyFile, "w") as f:
        for key in keys:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(key)


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
    light_char = service.getCharacteristics("2A6R")[0]
    light = light_char.read()
    light = byte_array_to_int(light)
    print(f"Light: {light} Units")

    return light


def read_sound(service):
    sound_char = service.getCharacteristics("2A6T")[0]
    sound = sound_char.read()
    sound = byte_array_to_int(sound)
    print(f"Sound: {sound} Units")

    return sound


def get_args():
    arg_parser = ArgumentParser(description="BLE IoT Sensor Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    args = arg_parser.parse_args()
    return args


if __name__ == "__main__":
    main(projectName, sensorName)