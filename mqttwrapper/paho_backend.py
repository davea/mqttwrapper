import os
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    for topic in userdata['topics']:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    replies = userdata['callback'](msg.topic, msg.payload, **userdata['kwargs'])
    if replies is not None:
        for topic, payload in replies:
            client.publish(topic, payload)


def run_script(callback, broker=None, topics=None, **kwargs):
    if not broker:
        broker = os.environ['MQTT_BROKER']
    if not topics:
        topics = os.environ['MQTT_TOPICS'].split(",")

    userdata = {
        'topics': topics,
        'callback': callback,
        'kwargs': kwargs
    }

    client = mqtt.Client(userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker.split("//")[1])
    client.loop_forever()
