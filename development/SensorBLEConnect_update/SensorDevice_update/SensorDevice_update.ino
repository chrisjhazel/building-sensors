// This code will read the temperature, humidity, pressure, and light data at specified intervals and print the data to the serial monitor
// Author: Chris Hazel
// Date: 2020.04.08
// Date Last Edit: 2021.03.08

#include <ArduinoBLE.h>
#include <Arduino_HTS221.h>
#include <Arduino_LPS22HB.h>
#include <Arduino_APDS9960.h>
#include <PDM.h>

//Set up the bluetooth characteristics
BLEService sensorService("181A");
BLEIntCharacteristic tempCharacteristic("2A6E", BLERead | BLENotify | BLEBroadcast);
BLEUnsignedIntCharacteristic humidCharacteristic("2A6F", BLERead | BLENotify | BLEBroadcast);
BLEUnsignedIntCharacteristic pressureCharacteristic("2A6D", BLERead | BLENotify | BLEBroadcast);
BLEIntCharacteristic lightCharacteristic("2B03", BLERead | BLENotify | BLEBroadcast); 
BLEIntCharacteristic soundCharacteristic("27C3", BLERead | BLENotify | BLEBroadcast); 

BLEService deviceInfo("a4ce5b72-d26c-436e-a451-fdcc16acd437");
//BLECharCharacteristic sensorName("2A00", BLERead | BLENotify | BLEBroadcast); //Set sensor specific name to each board
//BLECharCharacteristic sensorID("ec1d31fa-6dd7-45da-8dbe-5a7a727ae98a", BLERead | BLENotify | BLEBroadcast); //Set sensor specific ID for each board. Use ble address
BLEIntCharacteristic updateFreq("e74ca207-cfbc-4cbd-8339-e0e55144d648", BLERead | BLENotify | BLEBroadcast);
BLEFloatCharacteristic tempCal("e8be61a0-44e6-4220-bec7-7fa7f0f7be8f", BLERead | BLENotify | BLEBroadcast); 

// Set update time and calibration
// SET UPDATE FREQUENCY HERE
//
const int UPDATE_FREQUENCY = 60000; //Update every 60 seconds
//
//
const float TEMP_CALIBRATION = -6.5; //temperature calibration, may need to set periodically
long previousMillis = 0;

// buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// number of samples read
volatile int samplesRead;

//Set RGB pins numbers
#define rPin 22
#define gPin 23
#define bPin 24

// Set up device
void setup() {
  Serial.begin(9600);
  //while (!Serial); //This is used for local debugging purposes
  //Delay the sensor startups for a short period of time for when not connected to Serial Port
  delay(10000); //delay 10 seconds, probably longer than needed. Some time needed to warm up the sensor

    //Blink light to confirm ready
    //Initialize the LED light to confirm that the sensor is collecting data
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);

  if (!HTS.begin()) {
    Serial.println("Failed to initialize humidity temperature sensor!");
    while (1);
  }

  if (!BARO.begin()) {
    Serial.println("Failed to initialize pressure sensor!");
    while (1);
  }

  if (!APDS.begin()) {
    Serial.println("Failed to initialize ligth sensor!");
    while (1);
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

  //Turn on RGB LED to ensure it's working
  pinMode(rPin, OUTPUT);
  pinMode(gPin, OUTPUT);
  pinMode(bPin, OUTPUT);

  //Get the arduino address
  Serial.println("BLE Peripheral");
  String ardAddress = BLE.address();
  Serial.print("Arduino Address is: ");
  Serial.println(ardAddress);

  //Set up BLE name and ID
  String device_name = "1201Dellwood_Sensor1"; // Set individual sensor names for each board. Use ProjectName_Sensor#
  BLE.setLocalName("Arduino:Sensor");
  BLE.setDeviceName("1201Dellwood_Sensor1"); 

  //Set up BLE
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(tempCharacteristic);
  sensorService.addCharacteristic(humidCharacteristic);
  sensorService.addCharacteristic(pressureCharacteristic);
  sensorService.addCharacteristic(lightCharacteristic);
  sensorService.addCharacteristic(soundCharacteristic);
  
  BLE.setAdvertisedService(deviceInfo);
  deviceInfo.addCharacteristic(updateFreq);
  deviceInfo.addCharacteristic(tempCal);
  deviceInfo.addCharacteristic(sensorName);
  deviceInfo.addCharacteristic(sensorID);

  BLE.addService(sensorService);
  BLE.addService(deviceInfo);
  BLE.advertise();
  BLE.setConnectable(true);

  //Write the name and ID of the sensor
  //sensorName.writeValue(device_name);
  //sensorID.writeValue(ardAddress);

  tempCharacteristic.broadcast();
  humidCharacteristic.broadcast();
  pressureCharacteristic.broadcast();
  lightCharacteristic.broadcast();
  soundCharacteristic.broadcast();
  
  updateFreq.broadcast();
  tempCal.broadcast();
  //sensorName.broadcast();
  //sensorID.broadcast();

  updateFreq.writeValue(UPDATE_FREQUENCY);
  Serial.print("The update frequency is: ");
  Serial.print(UPDATE_FREQUENCY/1000);
  Serial.println(" seconds");

  tempCal.writeValue(TEMP_CALIBRATION);
  Serial.print("The temperature calibration is: ");
  Serial.print(TEMP_CALIBRATION);
  Serial.println(" °F");

}

//Loop script
void loop() {
  //Connect BLE
  BLEDevice central = BLE.central();
  if (central) {

    digitalWrite(LED_BUILTIN, HIGH); //Turn on the LED Light to show connection

    while (central.connected()) {
        long currentMillis = millis();
        if (currentMillis - previousMillis >= UPDATE_FREQUENCY) {
            previousMillis = currentMillis;
            updateReadings();
        }
    }

    //Blink LED light to confirm data collection
    digitalWrite(LED_BUILTIN, LOW); //Turn off the LED to show disconnection
    Serial.print("Disconnected from Central: ");
    Serial.println(central.address());

    }
}

int getTemperature(float calibration) {
    // Get the calibrated temperature as signed 16-bit int for BLE
    return (int) ((HTS.readTemperature() * 100) + (calibration * 100));
}

unsigned int getHumidity() {
    // Get the humidity as unsigned 16 bit int for BLE
    return (unsigned int) (HTS.readHumidity() * 100);
}

unsigned int getPressure() {
    // Get the pressure as unsigned 32 bit int for BLE
    return (unsigned int) (BARO.readPressure() * 1000 * 10);
}

int getColor() {
    // confirm that light sensor is working
    while (!APDS.colorAvailable()) {
        delay(2);
    }

    //Get the ambient light as unsigned 16 bit int for BLE
    int r, g, b, a;
    APDS.readColor(r, g, b, a);
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
    int temperatureAdj = ((temperature) * (1.8)) + 3200;
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
    unsigned int humidity = getHumidity();
    unsigned int pressure = getPressure();
    int light = getColor();
    int sound = getSound();

    tempCharacteristic.writeValue(temperature);
    int temperatureAdj = adjustTemperature(temperature);
    Serial.print(temperatureAdj/100);
    Serial.println(":TEMPERATURE-F");

    humidCharacteristic.writeValue(humidity);
    Serial.print(humidity/100);
    Serial.println(":HUMIDITY-%");

    pressureCharacteristic.writeValue(pressure);
    Serial.print(pressure/10000);
    Serial.println(":PRESSURE-Pa");

    lightCharacteristic.writeValue(light);
    Serial.print(light);
    Serial.println(":LIGHT");

    soundCharacteristic.writeValue(sound);
    Serial.print(sound);
    Serial.println(":SOUND");

    Serial.println();

    updateLEDPin(temperatureAdj, humidity);
}

void updateLEDPin(int temperature, int humidity) {
    //Use this function to update the RGB LED based on the temperature and humidity readings
    int highTemp = 80*100;
    int lowTemp = 60*100;
    int humThres = 50*100;

    //High temp + high humidity --> Yellow
    if ((temperature > highTemp) && (humidity > humThres)) {
            //Serial.println("YELLOW");
            digitalWrite(rPin, LOW);
            digitalWrite(gPin, LOW);
            digitalWrite(bPin, HIGH);
    }
    
    //Med temp + high humidity --> Green
    else if ((lowTemp < temperature) && (temperature < highTemp) && (humidity > humThres)) {
            //Serial.println("GREEN");
            digitalWrite(rPin, HIGH);
            digitalWrite(gPin, LOW);
            digitalWrite(bPin, HIGH);
        }

    //Low temp + high humidity --> Purple
    else if ((temperature < lowTemp) && (humidity > humThres)) {
            //Serial.println("PURPLE");
            digitalWrite(rPin, LOW);
            digitalWrite(gPin, HIGH);
            digitalWrite(bPin, LOW);
        }

    //High temp + low humidity --> Red
    else if ((temperature > highTemp) && (humidity < humThres)) {
            //Serial.println("RED");
            digitalWrite(rPin, LOW);
            digitalWrite(gPin, HIGH);
            digitalWrite(bPin, HIGH);
        }

    // Med temp + low humidity --> White
    else if ((lowTemp < temperature) && (temperature < highTemp) && (humidity < humThres)) {
            //Serial.println("WHITE");
            digitalWrite(rPin, LOW);
            digitalWrite(gPin, LOW);
            digitalWrite(bPin, LOW);
        }

    //Low temp + low humidity --> Blue
    else if ((temperature < lowTemp) && (humidity < humThres)) {
            //Serial.println("BLUE");
            digitalWrite(rPin, HIGH);
            digitalWrite(gPin, HIGH);
            digitalWrite(bPin, LOW);
        }
}
