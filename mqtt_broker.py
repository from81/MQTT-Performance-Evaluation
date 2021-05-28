import json
import logging
import time

import paho.mqtt.client as mqtt

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

# Client(client_id=””, clean_session=True, userdata=None, protocol=MQTTv311, transport=”tcp”)
client = mqtt.Client(client_id="3310-admin")
client.username_pw_set(username=credentials["username"], password=credentials["password"])
client.on_connect = on_connect
client.on_message = on_message
# client.on_publish = on_publish
client.on_subscribe = on_subscribe
client.on_log=on_log
# client.enable_logger(logging.getLogger(__name__))
client.connect(host="54.252.164.226", port=1883, keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# client.loop_forever()

# These functions implement a threaded interface to the network loop. 
# Calling loop_start() once, before or after connect*(), runs a thread in the background to call loop() automatically. 
# This frees up the main thread for other work that may be blocking. 
# This call also handles reconnecting to the broker. 
# Call loop_stop() to stop the background thread.
client.loop_start()
# client.loop_stop()

QOS = 0
intervals = [0, 0.01, 0.02, 0.05, 0.1, 0.5]
intervals_ms = [10, 20, 50, 100, 500]
DELAY = intervals[-1]
counter = 0

while True:
    client.publish(f"counter/{QOS}/{int(DELAY * 1000)}", qos=QOS, payload=str(counter))
    counter += 1
    time.sleep(DELAY)
