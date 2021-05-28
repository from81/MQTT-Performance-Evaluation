import json
import logging
import time
from typing import Dict

from paho.mqtt.client import Client

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

with open("env.json") as f:
    credentials = json.load(f)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected with result code: {rc}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe("request/qos")
    client.subscribe("request/delay")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logger.info(f"Topic: {msg.topic}\tQoS: {msg.qos}\tPayload: {str(msg.payload.decode())}")
    # msg methods = 'dup', 'info', 'mid', 'payload', 'properties', 'qos', 'retain', 'state', 'timestamp', 'topic'
    global DELAY, QOS
    if msg.topic == "request/qos":
        qos = int(msg.payload.decode())
        QOS = qos
    elif msg.topic == "request/delay":
        try:
            delay = int(msg.payload.decode())
            if delay in intervals_ms:
                delay /= 1000
        except:
            delay = float(msg.payload.decode())
        if delay in intervals:
            DELAY = delay

# def on_publish(client, obj, mid):
#     logger.info(f"Published: {mid}")

def on_subscribe(client, obj, mid, granted_qos):
    logger.info(f"Subscribed: {mid}\tQoS={granted_qos}")

def on_log(client, userdata, level, buf):
    logger.warning(f"Log: {buf}")

def create_client(id: int, credentials: Dict) -> Client:
    client_id = f"3310-controller-{id}"
    client = Client(client_id=client_id)
    client.username_pw_set(username=credentials["username"], password=credentials["password"])
    client.on_connect = on_connect
    client.on_message = on_message
    # client.on_publish = on_publish
    client.on_subscribe = on_subscribe
    client.on_log=on_log
    client.connect(host=credentials["ec2_host"], port=1883, keepalive=60)
    return client

intervals = [0, 0.01, 0.02, 0.05, 0.1, 0.5]
intervals_ms = [10, 20, 50, 100, 500]
DELAY = intervals[-1]
QOS = 0
counter = 0
clientID = 0
client = create_client(clientID, credentials)
logging.info(f"New client created\tQOS: {QOS}\tDelay: {DELAY}")
client.loop_start()

while True:
    client.publish(f"counter/{QOS}/{int(DELAY * 1000)}", qos=QOS, payload=str(counter))
    counter += 1
    time.sleep(DELAY)
