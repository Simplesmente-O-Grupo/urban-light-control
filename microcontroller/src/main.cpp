#include <Arduino.h>
#include <Wire.h>
#include <BH1750.h>
#include <queue.hpp>
#include <WiFi.h>
#include <time.h> // Para o timestamp NTP
#include <PubSubClient.h> // Para MQTT
#include <ArduinoJson.h>  // Para o payload

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

/* MQTT */
const char* mqtt_server = "192.168.241.131"; // Ex: "192.168.1.100" ou "broker.hivemq.com"
const int   mqtt_port = 1883;
const char* area_id = "1"; // <stationid> do seu tópico

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long publish_time = 0;
unsigned long publish_interval = 30 * 1000;

void publishMqttMessages() {
	// Nada para enviar, pula.
	if (cloud_buffer.size() == 0) return;

	if (!client.connected()) {
		Serial.println("Cliente MQTT desconectado. Ignorando publicação.");
		return;
	}

	// Monta o tópico: /area/<stationid>
	String topic = "/area/" + String(area_id);

	// Monta o Payload JSON
	JsonDocument doc;

	for (int i = 0; i < cloud_buffer.size(); i++) {
		CloudBufferItem it;

		cloud_buffer.pop(it);

		doc["values"][i] = it.lux;
		doc["timestamps"][i] = it.timestamp;
	}

	// Serializa o JSON para uma string
	String payload;
	serializeJson(doc, payload);
	Serial.print(payload.c_str());

	// Publica a mensagem
	if (client.publish(topic.c_str(), payload.c_str())) {
		Serial.print("Mensagem MQTT publicada [");
		Serial.print(topic);
		Serial.print("]: ");
		Serial.println(payload);
		cloud_buffer.clear();
	} else {
		Serial.println("Falha ao publicar mensagem MQTT.");
	}
}

// Função de Callback do MQTT
void mqttCallback(char* topic, byte* payload, unsigned int length) {
	Serial.print("Mensagem recebida [");
	Serial.print(topic);
	Serial.print("]: ");
	for (int i = 0; i < length; i++) {
		Serial.print((char)payload[i]);
	}
	Serial.println();
}

// Reconecta ao Broker MQTT
void reconnectMQTT() {
	while (!client.connected()) {
		Serial.print("Tentando conexao MQTT...");
		// Tenta conectar
		// (Pode adicionar usuário/senha aqui se precisar)
		if (client.connect(area_id)) {
			Serial.println("conectado!");
			// Você pode se inscrever em tópicos aqui, se necessário
			// client.subscribe("seu/topico/de/comando");
		} else {
			Serial.print("falha, rc=");
			Serial.print(client.state());
			Serial.println(" tentando novamente em 5 segundos");
			delay(5000);
		}
	}
}

void setup() {
	Serial.begin(9600);

	/* Inicializa o barramento I2C. */
	Wire.begin();

	lightMeter.begin();

	setupWiFi();

	setupNTP();

	// Configura o cliente MQTT
	client.setServer(mqtt_server, mqtt_port);
	client.setBufferSize(1024);
	client.setCallback(mqttCallback);

	Serial.println("==BEGIN==");
}

void loop() {
	unsigned long now = millis();

	// Garante que o MQTT está conectado
	if (!client.connected()) {
		reconnectMQTT();
	}
	client.loop();

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

	if ((cloud_buffer.size() > 0 && now - publish_time >= publish_interval) || cloud_buffer.isFull()) {
		publish_time = now;
		publishMqttMessages();
	}
}
