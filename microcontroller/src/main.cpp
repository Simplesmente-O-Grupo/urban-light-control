#include <Arduino.h>
#include <Wire.h>
#include <BH1750.h>
#include <queue.hpp>
#include <WiFi.h>
#include <time.h>

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

typedef struct {
	float lux;
	unsigned long timestamp;
} CloudBufferItem;

Queue<CloudBufferItem, 5> cloud_buffer;
/* Intervalo para enviar leituras para a nuvem em milisegundos. */
const long cloud_buffer_interval = 10 * 1000;
unsigned long cloud_buffer_time = 0;

float last_light_reading = 0;
unsigned long last_light_reading_timestamp = 0;
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

/* NTP */
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = -3 * 3600; // Offset GMT (Ex: -3 horas para Brasil)
const int   daylightOffset_sec = 0;     // Horário de verão (0 = desativado)

// Função para obter o timestamp Unix (segundos desde 1970)
unsigned long getTimestamp() {
	time_t now;
	struct tm timeinfo;
	if (!getLocalTime(&timeinfo)) {
		Serial.println("Falha ao obter hora local (NTP)");
		return 0;
	}
	time(&now);
	return (unsigned long)now;
}
// Sincroniza o relógio com o servidor NTP
void setupNTP() {
	Serial.println("Sincronizando hora com NTP...");
	configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

	// Espera até que o tempo seja sincronizado
	unsigned long startAttempt = millis();
	while (getTimestamp() < 1672531200) { // Espera até ser um timestamp válido (após 2023)
		delay(500);
		Serial.print(".");
		if (millis() - startAttempt > 10000) { // Timeout de 10s
			Serial.println("\nFalha ao sincronizar NTP. Reiniciando...");
			ESP.restart();
		}
	}
	Serial.println("\nNTP Sincronizado!");
}

void setup() {
	Serial.begin(9600);

	/* Inicializa o barramento I2C. */
	Wire.begin();

	lightMeter.begin();

	setupWiFi();

	setupNTP();

	Serial.println("==BEGIN==");
}

void loop() {
	unsigned long now = millis();

	if (now - last_light_reading_time >= last_light_reading_interval) {
		last_light_reading_time = now;
		last_light_reading = lightMeter.readLightLevel();
		last_light_reading_timestamp = getTimestamp();

		Serial.print("Light: ");
		Serial.print(last_light_reading);
		Serial.println(" lx");
	}

	if (now - cloud_buffer_time >= cloud_buffer_interval) {
		cloud_buffer_time = now;

		CloudBufferItem it;
		it.lux = last_light_reading;
		it.timestamp = last_light_reading_timestamp;
		cloud_buffer.push(it);

	}
}
