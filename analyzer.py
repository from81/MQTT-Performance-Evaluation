import json
import logging

import paho.mqtt.client as mqtt
import pandas as pd

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with open("env.json") as f:
    credentials = json.load(f)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected with result code: {rc}")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global data
    logger.info(f"Topic: {msg.topic}\tQoS: {msg.qos}\tPayload: {str(msg.payload.decode())}")
    data += [msg.timestamp, msg.topic, msg.qos, str(msg.payload.decode())],

# def on_publish(client, obj, mid):
#     logger.info(f"Published: {mid}")

def on_subscribe(client, obj, mid, granted_qos):
    logger.info(f"Subscribed: {mid}\tQoS={granted_qos}")

# def on_log(client, userdata, level, buf):
#     logger.warning(f"Log: {buf}")

# Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
client = mqtt.Client(client_id="3310-analyzer")
client.username_pw_set(username=credentials["username"], password=credentials["password"])
client.on_connect = on_connect
client.on_message = on_message
# client.on_publish = on_publish
client.on_subscribe = on_subscribe
# client.on_log=on_log
# client.enable_logger(logging.getLogger(__name__))
client.connect(host="54.252.164.226", port=1883, keepalive=60)
client.loop_start()

intervals = [0, 0.01, 0.02, 0.05, 0.1, 0.5]
qos = [0, 1, 2]
last_topic = None
data = []

for interval in intervals:
    for q in qos:
        if last_topic is not None:
            print(f"@@@@@@@@@@@@@@@@@@@@@@@@@@@@ {last_topic}")
            client.unsubscribe(last_topic)
        print("Data points collected:", len(data))

        current_len = len(data)
        topic = f"counter/{q}/{int(interval * 1000)}"
        client.subscribe(topic, qos=q)
        client.publish("request/qos", payload=q)
        client.publish("request/delay", payload=int(interval * 1000))
        last_topic = topic

        while len(data) < current_len + 1000:
            1 + 1

client.loop_stop()
df = pd.DataFrame(data, columns=['ts', 'topic', 'qos', 'payload'])
df.to_csv('stats.csv', index=False)