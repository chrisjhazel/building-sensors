import time
import math
import array

import board
import digitalio
import audiobusio
import neopixel_write
import neopixel
import adafruit_ble

# Import sensor functions
import adafruit_apds9960.apds9960
import adafruit_bmp280
import adafruit_lis3mdl
import adafruit_lsm6ds.lsm6ds33
import adafruit_sht31d

#from adafruit_ble.services.nordic import UARTService

from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# Import required BLE service functions
# These functions will send the information via BLE as a specific service
"""
#May not actually need these
from adafruit_ble_adafruit.temperature_service import TemperatureService
from adafruit_ble_adafruit.humidity_service import HumidityService
from adafruit_ble_adafruit.light_sensor_service import LightSensorService
from adafruit_ble_adafruit.barometric_pressure_service import BarometricPressureService
from adafruit_ble_adafruit.microphone_service import MicrophoneService
"""
##TEMPORARY UART IMPORTS
"""
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.services.circuitpython import CircuitPythonService
from adafruit_ble.services.circuitpython import CircuitPythonUUID
from adafruit_ble.uuid import UUID
from adafruit_ble.characteristics import Characteristic
"""

import _bleio as BLE

devSrvUUID = BLE.UUID(0x180A) #Geneic Device Information Service
deviceInfoService = BLE.Service(devSrvUUID)

nameUUID = BLE.UUID('3b1a0c8e-eebb-4e6b-b389-e47799000f21')
deviceTypeUUID = BLE.UUID('049a6341-e38b-4ea8-8189-7b0b209d3f8d')
updateFreqUUID = BLE.UUID('3669e347-ca4d-4782-8d61-46c7c5906a8d')
deviceName = BLE.Characteristic.add_to_service(deviceInfoService, nameUUID)
deviceType = BLE.Characteristic.add_to_service(deviceInfoService, deviceTypeUUID)
updateFreq = BLE.Characteristic.add_to_service(deviceInfoService, updateFreqUUID)

srvUUID = BLE.UUID(0x181A)
sensorService = BLE.Service(srvUUID)
print(sensorService)

tempUUID = BLE.UUID(0x2A6E)
tempCharacteristic = BLE.Characteristic.add_to_service(sensorService, tempUUID)
tempCharacteristic.BROADCAST
#tempCharacteristic.NOTIFY
#tempCharacteristic.READ
print(tempCharacteristic)

humidUUID = BLE.UUID(0x2A6F)
humidCharacteristic = BLE.Characteristic.add_to_service(
    sensorService, humidUUID)
humidCharacteristic.BROADCAST
#humidCharacteristic.NOTIFY
#humidCharacteristic.READ
print(humidCharacteristic)

pressureUUID = BLE.UUID(0x2A6D)
pressureCharacteristic = BLE.Characteristic.add_to_service(sensorService, pressureUUID)
pressureCharacteristic.BROADCAST
#pressureCharacteristic.NOTIFY
#pressureCharacteristic.READ
print(pressureCharacteristic)

lightUUID = BLE.UUID(0x2B03)
lightCharacateristic = BLE.Characteristic.add_to_service(sensorService, lightUUID)
lightCharacateristic.BROADCAST
print(lightCharacateristic)

soundUUID = BLE.UUID(0x27C3)
soundCharactersitic = BLE.Characteristic.add_to_service(sensorService, soundUUID)
soundCharactersitic.BROADCAST
print(soundCharactersitic)


"""
# Set up custom BLE services and characteristics 
#sensorService = adafruit_ble.services.Service(service = None)
sensorService = CircuitPythonService(service = None)
print(sensorService)
tempCharacteristic = Characteristic()
humidCharacteristic = Characteristic()
pressureCharacteristic = Characteristic()
lightCharacateristic = Characteristic()
soundCharactersitic = Characteristic()
updateFreq = Characteristic()
#sensorService.CircuitPythonUUID("181A")
"""



i2c = board.I2C()

apds9960 = adafruit_apds9960.apds9960.APDS9960(i2c)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)
lis3mdl = adafruit_lis3mdl.LIS3MDL(i2c)
lsm6ds33 = adafruit_lsm6ds.lsm6ds33.LSM6DS33(i2c)
sht31d = adafruit_sht31d.SHT31D(i2c)
microphone = audiobusio.PDMIn(board.MICROPHONE_CLOCK, board.MICROPHONE_DATA,
                              sample_rate=16000, bit_depth=16)

# Set update time and calibration
UPDATE_FREQUENCY = 10 # Update every 10 seconds
TEMP_CALIBRATION = -6.5 #temperature calibration due to board running a little hot. verify for different boards
previousTime = 0 #set time comparison for more accurate time keeping between readings

#Set up BLE services
"""
temperatureService = TemperatureService()
humidityService = HumidityService()
pressureService = BarometricPressureService()
lightService = LightSensorService()
soundService = MicrophoneService()
"""

# Funtions to get and send sensor data

def getTemp(tempChar):
    tempVal = bmp280.temperature + TEMP_CALIBRATION #Add the temperature calibration value
    tempAdj = (tempVal * 1.8) + 32 #Convert to fahrenheit 
    tempChar.value = tempAdj
    print("{}:TEMPERATURE-F".format(tempAdj))

    return tempAdj #return the temperature for the NeoPixel

def getHum(humChar):
    humVal = sht31d.relative_humidity
    humChar.value = humVal
    print("{}:HUMIDITY-%".format(humVal))

    return humVal #return the humidity for the NeoPixel

def getPress(pressChar):
    pressVal = bmp280.pressure
    pressAdj = pressVal*100 #Convert from hectopascals to pascals
    pressChar.value = pressAdj
    print("{}:PRESSURE-Pa".format(pressAdj))

def getLight(lightChar):
    lightVals = apds9960.color_data
    ambLight = lightVals[3]
    lightChar.value = ambLight
    print("{}:LIGHT-UNITS".format(ambLight))

def getSound(soundChar):
    samples = array.array('H', [0] * 160)
    microphone.record(samples, len(samples))
    soundVal = normalized_rms(samples)
    soundChar.value = soundVal
    print("{}:SOUND-UNITS".format(soundVal))

def normalized_rms(values):
    minbuf = int(sum(values) / len(values))
    return int(math.sqrt(sum(float(sample - minbuf) * (sample - minbuf) for sample in values) / len(values)))

def updateNeoPixel(temperature, humidity):
    highTemp = 80
    lowTemp = 60
    humThres = 50

    pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

    if temperature > highTemp and humidity > humThres:
        pixel[0] = (255, 255, 0) #Yellow
    
    elif lowTemp < temperature < highTemp and humidity > humThres:
        pixel[0] = (0, 255, 0) #Green
    
    elif temperature < lowTemp and humThres > humThres:
        pixel[0] = (255, 0, 255) #Purple
    
    elif temperature > highTemp and humidity < humThres:
        pixel[0] = (255, 0, 0) #Red
    
    elif lowTemp < temperature < highTemp and humidity < humThres:
        pixel[0] = (255, 255, 255) #White
    
    elif temperature < lowTemp and humidity < humThres:
        pixel[0] = (0, 0, 255) #Blue
    
    pixel.show()

def updateReadings():
    temp = getTemp(tempCharacteristic)
    hum = getHum(humidCharacteristic)
    getPress(pressureCharacteristic)
    getLight(lightCharacateristic)
    getSound(soundCharactersitic)
    print("===========================")

    updateNeoPixel(temp, hum)


sensorName = "Feather:Sensor"
address = BLE.adapter.address
print(address)

BLE.adapter.name = sensorName
print(BLE.adapter.name)
print(BLE.adapter.enabled)

#######
#Set device info service
#######
deviceName.value = sensorName
print(deviceName.value)
deviceType.value = "CircuitPython"
print(deviceType.value)
#updateFreq.value = UPDATE_FREQUENCY

# Set up the BLE advertising and connect to central
#BLE.name = ("Feather:Sensor")
#senAddress = BLE.address_bytes
#print(BLE.name)

uart = UARTService()
#advertisement = ProvideServicesAdvertisement(uart)
#print(advertisement)

#adv = adafruit_ble.advertising.Advertisement.complete_name = BLE.name
#advertisement = adafruit_ble.advertising.standard.ProvideServicesAdvertisement(uart)
#adv = adafruit_ble.advertising.Advertisement.shortName = BLE.name
#BLE.adapter.start_advertising(advertisement)
#time.sleep(10)

#dataPacket = (deviceName.value)
print(len(deviceName.value))
dataPacket = BLE.PacketBuffer(deviceName, buffer_size=20)
#dataPacket.readinto(deviceName.value)
dataPacket.write((deviceName.value))
print(type(dataPacket))

while True:
    BLE.adapter.start_advertising(dataPacket)
    print("Advertising: ", BLE.adapter.advertising)
    time.sleep(10)
    while not BLE.adapter.connected:
        pass
    while BLE.adapter.connected:
        #EMBED THIS IN A WHILE LOOP TO UPDATE WHILE CONNECTED
        currentTime = time.time()
        if currentTime - previousTime >= UPDATE_FREQUENCY:
            updateReadings()
            previousTime = currentTime
