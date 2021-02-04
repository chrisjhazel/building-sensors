// This code will read the temperature, humidity, pressure, and light data at specified intervals and print the data to the serial monitor
// Author: Chris Hazel
// Date: 2020.04.08
// Dat Last Edit: 2020.10.26

#include <Adafruit_APDS9960.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_LIS3MDL.h>
#include <Adafruit_LSM6DS33.h>
#include <Adafruit_SHT31.h>
#include <Adafruit_Sensor.h>
#include <bluefruit.h>
//#include <ArduinoBLE.h>
#include <Adafruit_NeoPixel.h>
#include <PDM.h>

//Adafruit Bluefruit Feather Sense Libraries
Adafruit_APDS9960   apds9960;   // proximity, light, color, gesture
Adafruit_BMP280     bmp280;     // temperautre, barometric pressure
Adafruit_LIS3MDL    lis3mdl;    // magnetometer
Adafruit_LSM6DS33   lsm6ds33;   // accelerometer, gyroscope
Adafruit_SHT31      sht30;      // humidity
AdafruitBluefruit    BLE;        // bluetooth

//Set up the bluetooth characteristics
BLEService sensorService = BLEService('7fa1b255 - 4049 - 4c72 - a942 - dd021a2113cf'); //Keep for now since this is the expected UUID for environmental sensor
//sensorService.begin();

//Set the BLE UUIDs
ble_uuid_t tempUUID = BLE.BLEUuid(4d7b7444 - ba14 - 43ca - 8dae-be33581315f6);

BLECharacteristic tempCharacteristic = BLECharacteristic(tempUUID);
BLECharacteristic humidCharacteristic = BLECharacteristic('17b70fb3 - 02a7 - 4fcd - 8bf3 - 0c1880f73189');
BLECharacteristic pressureCharacteristic = BLECharacteristic('f1455524 - 94ad - 4535 - 9385 - 7c04117c1027');
BLECharacteristic lightCharacteristic = BLECharacteristic('ca214582 - d111 - 4e6d - 8859 - 939e0beec9aa');
BLECharacteristic soundCharacteristic = BLECharacteristic('a7895b70 - 6bc1 - 4d99 - bdd4 - d69d3297caa8');
BLECharacteristic updateFreq = BLECharacteristic('9a1b5df6 - 824b - 4381 - 8ad7 - 8005bd53e281');



// Set update time and calibration
const int UPDATE_FREQUENCY = 10000; //Update every 10 seconds
const float TEMP_CALIBRATION = -6.5; //temperature calibration, may need to set periodically
long previousMillis = 0;

// buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// number of samples read
volatile int samplesRead;

void setup() {
  Serial.begin(9600);
  //while (!Serial);
  //Delay the sensor startups for a short period of time for when not connected to Serial Port
  delay(10000); //delay 10 seconds, probably longer than needed

    //Blink light to confirm ready
    //Initialize the LED light to confirm that the sensor is collecting data
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);

  if (!bmp280.begin()) {
    Serial.println("Failed to initialize temperature pressure sensor!");
    while (1);
  }

  if (!sht30.begin()) {
    Serial.println("Failed to initialize humidity sensor!");
    while (1);
  }

  if (!apds9960.begin()) {
      Serial.println("Failed to initialize ligth sensor!");
      while (1);
  apds9960.enableColor(true);
  }

  // configure the data receive callback
  PDM.onReceive(onPDMdata);

  // optionally set the gain, defaults to 20
  // PDM.setGain(30);

  // initialize PDM with:
  // - one channel (mono mode)
  // - a 16 kHz sample rate
  if (!PDM.begin(1, 16000))
  {
    Serial.println("Failed to start PDM!");
    while (1);
  }

  if (!BLE.begin()) {
    Serial.println("Could not start BLE!");
    while (1);
  }

/*
Add section to control RGB LED based on conditions
    const int rPin = 22;
    const int gPin = 23;
    const int bPin = 24;

    pinMode(22, OUTPUT);
    pinMode(23, OUTPUT);
    pinMode(24, OUTPUT);

    */

  //Set up BLE
  /*
  BLE.setLocalName("Arduino:Sensor");
  BLE.setDeviceName("Arduino:Sensor");
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(tempCharacteristic);
  sensorService.addCharacteristic(humidCharacteristic);
  sensorService.addCharacteristic(pressureCharacteristic);
  sensorService.addCharacteristic(lightCharacteristic);
  sensorService.addCharacteristic(soundCharacteristic);
  sensorService.addCharacteristic(updateFreq);

  BLE.addService(sensorService);
  BLE.advertise();
  */
  Serial.println("BLE Peripheral");

  ble_gap_addr_t addr = BLE.getAddr();
  //NRF_LOG_RAW_INFO("\n%02X:%02X:%02X:%02X:%02X:%02X\n", &addr.addr[0], &addr.addr[1], &addr.addr[2], &addr.addr[3], &addr.addr[4], &addr.addr[5]);

  //Serial.print(macAddr);
  //uint32_t err_code = sd_ble_gap_address_get(&addr);
  //APP_ERROR_CHECK(err_code);

  //NRF_LOG_RAW_INFO("\n%02X:%02X:%02X:%02X:%02X:%02X\n",
  //char macAddr[20];
  //sprintf(macAddr, "%02x:%02x:%02x:%02x:%02x:%02x", &addr.addr[0], &addr.addr[1], &addr.addr[2], &addr.addr[3], &addr.addr[4], &addr.addr[5]);
  //Serial.print(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]);
  //Serial.print(addr);

  Serial.print("Arduino Address is: ");
  //Serial.println(ardAddress);

  //Set the characteristic properties
tempCharacteristic.setProperties(CHR_PROPS_WRITE);
humidCharacteristic.setProperties(CHR_PROPS_WRITE);
pressureCharacteristic.setProperties(CHR_PROPS_WRITE);
lightCharacteristic.setProperties(CHR_PROPS_WRITE);
soundCharacteristic.setProperties(CHR_PROPS_WRITE);

  //Set bluetooth connection
  BLE.Advertising.start();
  //BLE.setAdvertisingInterval(10000);
  //BLE.advertise();
  //BLE.setConnectable(true);

/*
  tempCharacteristic.broadcast();
  humidCharacteristic.broadcast();
  pressureCharacteristic.broadcast();
  lightCharacteristic.broadcast();
  soundCharacteristic.broadcast();
  updateFreq.broadcast();
  */

  updateFreq.write32(UPDATE_FREQUENCY);
  Serial.print("The update frequency is: ");
  Serial.print(UPDATE_FREQUENCY / 1000);
  Serial.println(" seconds");
}

void loop() {

  //Connect BLE
  //BLEDevice central = BLE.central();
  uint16_t central = BLE.connected();
  Serial.print(central);
  uint16_t cenAddr = BLE.connHandle();
  Serial.print(cenAddr);
  /*
  if (!central) {
    BLE.advertise();
    Serial.println("Not Connected");
  }*/
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(BLE.connected(cenAddr));
    //Serial.print("RSSI = ");
    //int rssiVal = BLE.rssi();
    //Serial.println(rssiVal);

    digitalWrite(LED_BUILTIN, HIGH); //Turn on the LED Light to show connection

    while (BLE.connected(cenAddr)) {
        long currentMillis = millis();
        if (currentMillis - previousMillis >= UPDATE_FREQUENCY) {
            previousMillis = currentMillis;
            updateReadings();
        }
    }

    //Blink LED light to confirm data collection
    digitalWrite(LED_BUILTIN, LOW); //Turn off the LED to show disconnection
    Serial.print("Disconnected from Central: ");
    //Serial.println(central.address());

    }
}

int getTemperature(float calibration) {
    // Get the calibrated temperature as signed 16-bit int for BLE
    return (int) (bmp280.readTemperature() * 100) + (int) (calibration * 100);
}

unsigned int getHumidity() {
    // Get the humidity as unsigned 16 bit int for BLE
    return (int) (sht30.readHumidity() * 100);
}

unsigned int getPressure() {
    // Get the pressure as unsigned 32 bit int for BLE
    return (int) (bmp280.readPressure() * 1000 * 10);
}

int getColor() {
    // confirm that light sensor is working
    while (!apds9960.colorDataReady()) {
        delay(2);
    }

    //Get the ambient light as unsigned 16 bit int for BLE
    uint16_t r, g, b, a;
    apds9960.getColorData(&r, &g, &b, &a);
    return a;
}

int getSound() {
    //Get the sound data as int
    //initialize sound variables
    int n = 0, sound;
    float Sum = 0.0;

    //Gather sound data
    for (int j = 0; j < 100; j++) {
        //If no new samples, wait a tick
        while (!samplesRead) {
            delay(2);
        }
        if (samplesRead) {
            for (int i = 0; i < samplesRead; i++) {
                Sum = Sum + abs(sampleBuffer[i]);
                n++;
            }
            //clear the read count
            samplesRead = 0;
        }
    }
    return sound = Sum / n;
}

int adjustTemperature(int temperature) {
    int temperatureAdj = (temperature/100) * (9/5) + 32;
    return temperatureAdj;
}

void onPDMdata()
{
  // query the number of bytes available
  int bytesAvailable = PDM.available();

  // read into the sample buffer
  PDM.read(sampleBuffer, bytesAvailable);

  // 16-bit, 2 bytes per sample
  samplesRead = bytesAvailable / 2;
}

void updateReadings() {
    int temperature = getTemperature(TEMP_CALIBRATION);
    int humidity = getHumidity();
    int pressure = getPressure();
    int light = getColor();
    int sound = getSound();

    tempCharacteristic.write32(temperature);
    int temperatureAdj = adjustTemperature(temperature);
    Serial.print(temperatureAdj);
    Serial.println(":TEMPERATURE-F");

    humidCharacteristic.write32(humidity);
    Serial.print(humidity/100);
    Serial.println(":HUMIDITY-%");

    pressureCharacteristic.write32(pressure);
    Serial.print(pressure/10000);
    Serial.println(":PRESSURE-Pa");

    lightCharacteristic.write32(light);
    Serial.print(light);
    Serial.println(":LIGHT");

    soundCharacteristic.write32(sound);
    Serial.print(sound);
    Serial.println(":SOUND");

    Serial.println();

    //updateLEDPin(temperatureAdj, (humidity/100));
}
/*
void updateLEDPin(temperature, humidity) {
    //Use this function to update the RGB LED based on the temperature and humidity readings
    const int highTemp = 75;
    const int lowTemp = 60;
    const int humThres = 50;

    //High temp + high humidity --> Yellow
    if temperature > highTemp && humidity > humThres {
            digitalWrite(rPin, HIGH);
            digitalWrite(gPin, HIGH);
            digitalWrite(bPin, LOW);
    }
    
    //Med temp + high humidity --> Green
    if lowTemp < temperature < highTemp && humidity > humThres {
            digitalWrite(rPin, LOW);
            digitalWrite(gPin, HIGH);
            digitalWrite(bPin, LOW);
        }

    //Low temp + high humidity --> Purple
    if temperature < lowTemp && humidity > humThres {
            digitalWrite(rPin, HIGH);
            digitalWrite(gPin, LOW);
            digitalWrite(bPin, HIGH);
        }

    //High temp + low humidity --> Red
    if temperature > highTemp && humidity < humThres {
            digitalWrite(rPin, HIGH);
            digitalWrite(gPin, LOW);
            digitalWrite(bPin, LOW);
        }

    // Med temp + low humidity --> White
    if lowTemp < temperature < highTemp && humidity < humThres {
            digitalWrite(rPin, HIGH);
            digitalWrite(gPin, HIGH);
            digitalWrite(bPin, HIGH);
        }

    //Low temp + low humidity --> Blue
    if temperature < lowTemp && humidity < humThres {
            digitalWrite(rPin, LOW);
            digitalWrite(gPin, LOW);
            digitalWrite(bPin, HIGH);
        }
}
*/
