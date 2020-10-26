// This code will read the temperature, humidity, pressure, and light data at specified intervals and print the data to the serial monitor
// Author: Chris Hazel
// Date: 2020.04.08

#include <ArduinoBLE.h>
#include <Arduino_HTS221.h>
#include <Arduino_LPS22HB.h>
#include <Arduino_APDS9960.h>
#include <PDM.h>

//Set up the bluetooth characteristics
BLEService nanoService("19b10010-e8f2-537e-4f6c-d104768a1214");
BLEFloatCharacteristic tempCharacteristic("19b10011-e8f2-537e-4f6c-d104768a1214", BLERead | BLENotify | BLEBroadcast);
BLEFloatCharacteristic humidCharacteristic("19b10012-e8f2-537e-4f6c-d104768a1214", BLERead | BLENotify | BLEBroadcast);
BLEFloatCharacteristic pressureCharacteristic("19b10013-e8f2-537e-4f6c-d104768a1214", BLERead | BLENotify | BLEBroadcast);
BLEIntCharacteristic lightCharacteristic("19b10014-e8f2-537e-4f6c-d104768a1214", BLERead | BLENotify | BLEBroadcast);
BLEFloatCharacteristic soundCharacteristic("19b10015-e8f2-537e-4f6c-d104768a1214", BLERead | BLENotify | BLEBroadcast);

// buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// number of samples read
volatile int samplesRead;

void setup() {
  Serial.begin(9600);
  while (!Serial);


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

  //Initialize the LED light to confirm that the sensor is collecting data
  pinMode(LED_BUILTIN, OUTPUT);

  //Set up BLE
  BLE.setLocalName("Arduino:Sandie");
  BLE.setDeviceName("Arduino:Sandie");
  BLE.setAdvertisedService(nanoService);
  nanoService.addCharacteristic(tempCharacteristic);
  nanoService.addCharacteristic(humidCharacteristic);
  nanoService.addCharacteristic(pressureCharacteristic);
  nanoService.addCharacteristic(lightCharacteristic);
  nanoService.addCharacteristic(soundCharacteristic);

  BLE.addService(nanoService);
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

    while (central.connected()) {



      //Blink LED light to confirm data collection
      digitalWrite(LED_BUILTIN, HIGH);

      float temperatureAdj = HTS.readTemperature();
      float temperature = (temperatureAdj - (6.5));//*(9/5)) + 32;
      float humidity = HTS.readHumidity();
      float pressure = BARO.readPressure();
      int r, g, b, light;

      //initialize sound variables
      int n = 0;
      float Sum = 0.0, sound;

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
      sound = Sum / n;

      //If not able to read the light sensor, delay for a bit
      while (! APDS.colorAvailable()) {
        delay(2);
      }

      APDS.readColor(r, g, b, light); //will only read the ambient light component

      delay(1000);
      digitalWrite(LED_BUILTIN, LOW);

      tempCharacteristic.writeValue(temperature);
      Serial.print(temperature);
      Serial.println(":TEMPERATURE-F");

      humidCharacteristic.writeValue(humidity);
      Serial.print(humidity);
      Serial.println(":HUMIDITY-%");

      pressureCharacteristic.writeValue(pressure);
      Serial.print(pressure);
      Serial.println(":PRESSURE-PSI");

      lightCharacteristic.writeValue(light);
      Serial.print(light);
      Serial.println(":LIGHT-LUX");

      soundCharacteristic.writeValue(sound);
      Serial.print(sound);
      Serial.println(":SOUND-units");

      Serial.println();

      //repeat process every 4 seconds, so that record happens every 5 seconds
      delay(4000);
    }
  }
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
