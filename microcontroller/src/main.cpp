#include <Arduino.h>
#include <Wire.h>
#include <BH1750.h>

BH1750 lightMeter;

void setup() {
	Serial.begin(9600);

	/* Inicializa o barramento I2C. */
	Wire.begin();

	lightMeter.begin();
	Serial.println("BEGIN");
}

void loop() {
	float lux = lightMeter.readLightLevel();
	Serial.print("Light: ");
	Serial.print(lux);
	Serial.println(" lx");
	delay(1000);
}
