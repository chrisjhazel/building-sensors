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

    //Initialize the LED light to confirm that the sensor is collecting data
    pinMode(LED_BUILTIN, OUTPUT);

    //PRINT THE HEADER
    //Serial.println("Temperature, Humidity, Pressure, Light");

}

void loop() {

    //Blink LED light to confirm data collection
    digitalWrite(LED_BUILTIN, HIGH);
    
    float temperature = HTS.readTemperature(FAHRENHEIT);
    float humidity = HTS.readHumidity();
    float pressure = BARO.readPressure(PSI);
    int r, g, b, light; //Set to the 0 incase the light cannot be read

    if (APDS.colorAvailable())
        delay(5);
    
    APDS.readColor(r, g, b, light); //will only read the ambient light component

    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);

    Serial.print(temperature);
    Serial.println(":TEMPERATURE-F");
    
    Serial.print(humidity);
    Serial.println(":HUMIDITY-%:");
    
    Serial.print(pressure);
    Serial.println(":PRESSURE-PSI:");
    
    Serial.print(light);
    Serial.println(":LIGHT-LUX:");
    
    Serial.println();


/*
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
    Serial.println(" units"); //need to clarify the units of abient light, may be lux

    Serial.print("Sound Average = ");
    Serial.print(soundAvg);
    Serial.println(" dB");

    Serial.println("------");

*/
    //repeat process every 4 seconds, so that record happens every 5 seconds
    delay(3995);
}
