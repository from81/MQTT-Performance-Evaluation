import json
import logging
import time

from paho.mqtt.client import Client, MQTTv31
import pandas as pd

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with open("env_partner.json") as f:
    credentials = json.load(f)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected with result code: {rc}")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global data
    logger.info(f"Topic: {msg.topic}\tQoS: {msg.qos}\tPayload: {str(msg.payload.decode())}\tData points: {len(data)}")
    data += [msg.timestamp, msg.topic, msg.qos, str(msg.payload.decode())],

def on_publish(client, obj, mid):
    logger.info(f"Published: {mid}")

def on_subscribe(client, obj, mid, granted_qos):
    logger.info(f"Subscribed: {mid}\tQoS={granted_qos}")

def on_log(client, userdata, level, buf):
    logger.warning(f"Log: {buf}")


# Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
client = Client(client_id="3310-analyzer", protocol=MQTTv31)
client.username_pw_set(username=credentials["username"], password=credentials["password"])
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_log = on_log

client.connect(host=credentials["ec2_host"], port=1883, keepalive=60)

intervals = [0, 0.01, 0.02, 0.05, 0.1, 0.5]
qos = [0, 1, 2]
last_topic = None
data = []

# subscribe to all counter topics in advance
for interval in intervals[::-1]:
    for q in qos:
        topic = f"counter/{q}/{int(interval * 1000)}"
        client.subscribe(topic, qos=q)

client.loop_start()

for interval in intervals[::-1]:
    for q in qos:
        if last_topic is not None:
            # unsubscribe topics once enough data points are collected
            logger.info(f"Unsubscribed: {last_topic}")
            client.unsubscribe(last_topic)

        time.sleep(1)

        # request QOS and Delay change
        client.publish("request/qos", payload=q, qos=1)
        time.sleep(0.5)
        client.publish("request/delay", payload=int(interval * 1000), qos=1)
        last_topic = f"counter/{q}/{int(interval * 1000)}"

        # collect data for 120s
        current_time = time.time()
        counter = 0
        while time.time() - current_time <= 120:
            counter += 1


client.loop_stop()
df = pd.DataFrame(data, columns=['ts', 'topic', 'qos', 'payload'])
df.to_csv('stats_partner_broker.csv', index=False)