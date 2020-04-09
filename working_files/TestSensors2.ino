// This code will read the temperature, humidity, pressure, and light data at specified intervals and print the data to the serial monitor
// Author: Chris Hazel
// Date: 2020.04.08

#include <Arduino_HTS221.h>
#include <Arduino_LPS22HB.h>
#include <Arduino_APDS9960.h>

void setup() {
    Serial.begin(9600);
    while (!Serial);

    if (!HTS.begin()) {
        Serial.println("Failed to initialize humidity temperature sensor!");
        while(1);
    }

    if (!BARO.begin()) {
        Serial.println("Failed to initialize pressure sensor!");
        while(1);
    }

    if (!APDS.begin()){
        Serial.println("Failed to initialize ligth sensor!");
        while(1);
    }
}

void loop() {
    float temperature = HTS.readTemperature(FAHRENHEIT);
    float humidity = HTS.readHumidity();
    float pressure = BARO.readPressure(PSI);
    int r, g, b, light = 0; //Set to the 0 incase the light cannot be read

    if (APDS.colorAvailable())
        APDS.readColor(r, g, b, light); //will only read the ambient light component

    Serial.print("Temperature = ");
    Serial.print(temperature);
    Serial.println(" F");

    Serial.print("Humidity = ");
    Serial.print(humidity);
    Serial.println(" %");

    Serial.print("Pressure = ");
    Serial.print(pressure);
    Serial.println(" PSI");

    Serial.print("Light = ");
    Serial.print(light);
    Serial.print("units"); //need to clarify the units of abient light, may be lux


    //repeat process every 5 seconds
    delay(5000);
}