import paho.mqtt.client as mqtt
from paho.mqtt.enums import MQTTProtocolVersion
import json
from time import sleep
from database import engine, SessionLocal
from models import Base, Reading
import os
from time import sleep
from datetime import datetime

print("Sleeping for 10 seconds to wait for db setup...")
sleep(10)

print("Creating ORM SQL Tables..")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Conectado: {reason_code}")
    # Me inscrevo em todos os tópicos sobre clima
    client.subscribe("/area/#")

# TODO: Avisar o time do ESP para usar este formato:
# Tópico MQTT: /weather/<stationid>
# Corpo:
# {
#   "sensor": <sensor device id>,
#   "unit": <measure id>",
#   "reading_values: [
#        <valor da medida, pode ser inteiro ou decimal>,
#       . . .
#    ],
#   "reading_timestamps": [
#        <timestamp das medidas>,
#       . . .
#    ]
# }
# Simplesmente imprime a mensagem como texto.
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    topic = msg.topic.split('/')[-1]
    print(f"GOT MESSAGE {payload}")

    if topic.isnumeric():
        areaId = int(topic)
    else:
        AreaId = None

    try:
        sensor_id = int(payload["sensor"])
        measure_type_id = 1
        readings = []
        # É para values e timestamps terem o mesmo tamanho,
        for i in range(0, len(payload["values"])):
            readings.append({
                "value": float(payload["values"][i]),
                "intensity": float(payload["intensities"][i]),
                "timestamp": int(payload["timestamps"][i])
            })

    except:
        print(f"ERRO! Leitura mal formatada {payload}")
        return

    session = SessionLocal()
    session.begin()
    for reading in readings:
        print(reading)
        session.add(Reading(sensor_id=sensor_id, measure_type_id=measure_type_id, value=reading['value'], intensity=reading['intensity'], timestamp=datetime.fromtimestamp(reading['timestamp'],)))
    session.commit()
    session.close()

try:
    user_name = os.environ["MQTT_CLIENT_USER"]
    user_pass = os.environ["MQTT_CLIENT_PASSWORD"]
except KeyError:
    print("credentials not supplied in environment variables. Going unauthenticated...")
    user_name = None
    user_pass = None

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, protocol=MQTTProtocolVersion.MQTTv5)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
#mqttc.username_pw_set(user_name, user_pass)

connected = False

while(not connected):
    try:
        mqttc.connect("mosquitto", 1883, 60, '', 0, True)
        connected = True
    except ConnectionRefusedError:
        print("Failed to connect. Retrying...")
        sleep(5)

mqttc.loop_forever()
