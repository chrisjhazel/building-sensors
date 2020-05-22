// This code will read the temperature, humidity, pressure, and light data at specified intervals and print the data to the serial monitor
// Author: Chris Hazel
// Date: 2020.04.08

#include <Arduino_HTS221.h>
#include <Arduino_LPS22HB.h>
#include <Arduino_APDS9960.h>
#include <PDM.h>
//#include <ArduinoBLE.h>

// buffer to read samples into, each sample is 16-bits
short sampleBuffer[256];

// number of samples read
volatile int samplesRead;

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
        //while(1);
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
        while (1)
            ;
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
    int r, g, b, light;

    //initialize sound variables
    int n=0;
    float Sum=0.0, sound;

    //Gather sound data
    for (int j=0; j<100; j++){
        //If no new samples, wait a tick
        while(!samplesRead){
            delay(2);
        }
        if (samplesRead){
            for(int i=0; i<samplesRead; i++){
                Sum = Sum + abs(sampleBuffer[i]);
                n++;
            }
            //clear the read count
            samplesRead = 0;
        }
    }
    sound = Sum/n;

    //If not able to read the light sensor, delay for a bit
    while (! APDS.colorAvailable()){
        delay(2);
    }
    
    APDS.readColor(r, g, b, light); //will only read the ambient light component

    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);

    Serial.print(temperature);
    Serial.println(":TEMPERATURE-F");
    
    Serial.print(humidity);
    Serial.println(":HUMIDITY-%");
    
    Serial.print(pressure);
    Serial.println(":PRESSURE-PSI");
    
    Serial.print(light);
    Serial.println(":LIGHT-LUX");
    
    Serial.print(sound);
    Serial.println(":SOUND-units");

    Serial.println();

    //repeat process every 4 seconds, so that record happens every 5 seconds
    delay(1000);
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