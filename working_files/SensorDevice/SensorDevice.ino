// This code will read the temperature, humidity, pressure, and light data at specified intervals and print the data to the serial monitor
// Author: Chris Hazel
// Date: 2020.04.08
// Dat Last Edit: 2020.10.26

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
BLEIntCharacteristic lightCharacteristic("adb5976d-f756-43ca-8a32-1a6cdf97601f", BLERead | BLENotify | BLEBroadcast);
BLEIntCharacteristic soundCharacteristic("fbfebdd5-f415-43c9-b5d5-c3094f2c86be", BLERead | BLENotify | BLEBroadcast);
BLEIntCharacteristic updateFreq("2A6B", BLERead | BLENotify | BLEBroadcast);

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
  Serial.println("BLE Peripheral");

  String ardAddress = BLE.address();
  
  Serial.print("Arduino Address is: ");
  Serial.println(ardAddress);

  //Set bluetooth connection
  BLE.setAdvertisingInterval(10000);
  BLE.advertise();
  BLE.setConnectable(true);

  tempCharacteristic.broadcast();
  humidCharacteristic.broadcast();
  pressureCharacteristic.broadcast();
  lightCharacteristic.broadcast();
  soundCharacteristic.broadcast();
  updateFreq.broadcast();

  updateFreq.writeValue(UPDATE_FREQUENCY);
  Serial.print("The update frequency is: ");
  Serial.print(UPDATE_FREQUENCY/1000);
  Serial.println(" seconds");

}

void loop() {

  //Connect BLE
  BLEDevice central = BLE.central();
  /*
  if (!central) {
    BLE.advertise();
    Serial.println("Not Connected");
  }*/
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    Serial.print("RSSI = ");
    int rssiVal = BLE.rssi();
    Serial.println(rssiVal);

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
    return (int) (HTS.readTemperature() * 100) + (int) (calibration * 100);
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
    unsigned int humidity = getHumidity();
    unsigned int pressure = getPressure();
    int light = getColor();
    int sound = getSound();

    tempCharacteristic.writeValue(temperature);
    int temperatureAdj = adjustTemperature(temperature);
    Serial.print(temperatureAdj);
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

    updateLEDPin(temperatureAdj, (humidity/100));
}

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