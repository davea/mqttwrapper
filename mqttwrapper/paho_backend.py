import os
import logging
import paho.mqtt.client as mqtt

log = logging.getLogger("mqttwrapper.paho_backend")

def on_connect(client, userdata, flags, rc):
    log.debug("Connected")
    for topic in userdata['topics']:
        client.subscribe(topic)
        log.debug("Subscribed to %s", topic)

def on_message(client, userdata, msg):
    log.debug("Received message on %s", msg.topic)
    replies = userdata['callback'](msg.topic, msg.payload, **userdata['kwargs'])
    log.debug("Callback completed.")
    if replies is not None:
        log.debug("Received %s replies", len(replies))
        for topic, payload in replies:
            log.debug("Publishing '%s' to %s", payload, topic)
            client.publish(topic, payload)
            log.debug("Published '%s' to %s", payload, topic)


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
