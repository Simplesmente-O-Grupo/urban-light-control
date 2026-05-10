#include <Arduino.h>
#include <Wire.h>
#include <BH1750.h>
#include <queue.hpp>
#include <WiFi.h>

BH1750 lightMeter;


/* A principal lógica por trás da leitura do sensor é que
 * a frequência de leitura é diferente da frequência que
 * enviaremos para a nuvem.
 *
 * O motivo para isto é que não faz sentido monitorar
 * alterações de temperaturas em intervalos de segundos,
 * mas tal frequência é necessária para controlar o brilho
 * dos LEDs.
 */

Queue<float, 5> cloud_buffer;
/* Intervalo para enviar leituras para a nuvem em milisegundos. */
volatile const long cloud_buffer_interval = 10 * 1000;
unsigned long cloud_buffer_time = 0;

float last_light_reading = 0;
unsigned long last_light_reading_time = 0;
unsigned long last_light_reading_interval = 2000;


/* WiFi */
const char *wifi_ssid = "hrdstn-1";
const char *wifi_pass = "hewhowatches";
// Conecta ao WiFi
void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando em ");
  Serial.println(wifi_ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(wifi_ssid, wifi_pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Conectado!");
  Serial.print("Endereco IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
	Serial.begin(9600);

	/* Inicializa o barramento I2C. */
	Wire.begin();

	lightMeter.begin();

	setupWiFi();

	Serial.println("==BEGIN==");
}

void loop() {
	unsigned long now = millis();

	if (now - last_light_reading_time >= last_light_reading_interval) {
		last_light_reading_time = now;
		last_light_reading = lightMeter.readLightLevel();

		Serial.print("Light: ");
		Serial.print(last_light_reading);
		Serial.println(" lx");
	}

	if (now - cloud_buffer_time >= cloud_buffer_interval) {
		cloud_buffer_time = now;

		cloud_buffer.push(last_light_reading);

	}
}
