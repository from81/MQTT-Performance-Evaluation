import json
import logging
# from multiprocessing import Process
import os
import random
from threading import Thread
import time
from typing import Dict

from paho.mqtt.client import Client, MQTTv31

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

intervals = [0, 0.01, 0.02, 0.05, 0.1, 0.5]
intervals_ms = [10, 20, 50, 100, 500]
DELAY = intervals[-1]
QOS = 0

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
    global DELAY, QOS, child_process, credentials
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

            # create a new publisher and attach it to the controller
            p = Thread(target=create_publisher, kwargs={'qos':QOS, 'delay':DELAY, 'credentials':credentials})
            p.start()
            # p.join()

def on_publish(client, obj, mid):
    logger.info(f"Published: {mid}")

def on_subscribe(client, obj, mid, granted_qos):
    logger.info(f"Subscribed: {mid}\tQoS={granted_qos}")

def on_log(client, userdata, level, buf):
    logger.warning(f"Log: {buf}")

def create_client(credentials: Dict) -> Client:
    client = Client(client_id="3310-controller2", protocol=MQTTv31)
    client.username_pw_set(username=credentials["username"], password=credentials["password"])
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_log=on_log
    client.connect(host=credentials["ec2_host"], port=1883, keepalive=1000)
    return client

def create_publisher(qos, delay, credentials):
    """creates a publisher client for sending counter messages"""
    publisher_id = random.randint(0, 1000)
    publisher = Client(client_id=f"3310-publisher-{publisher_id}", protocol=MQTTv31)
    publisher.username_pw_set(username=credentials["username"], password=credentials["password"])
    publisher.on_log = on_log
    publisher.connect(host=credentials["ec2_host"], port=1883, keepalive=60)
    logger.info(f'new publisher created with ID {publisher_id}')
    publisher.loop_start()
    time.sleep(1)

    start_time = time.time()
    i = 0
    while time.time() - start_time <= 120:
        mi = publisher.publish(f"counter/{qos}/{int(delay * 1000)}", qos=qos, payload=str(i))
        mi.wait_for_publish()
        time.sleep(delay)
        i += 1
    publisher.loop_stop()


with open("env.json") as f:
    credentials = json.load(f)

client = create_client(credentials)
client.credentials = credentials
client.loop_forever()
