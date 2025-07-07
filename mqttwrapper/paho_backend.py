import os
import logging
import paho.mqtt.client as mqtt
import threading

log = logging.getLogger("mqttwrapper.paho_backend")

def on_connect(client, userdata, flags, rc):
    log.debug("Connected")
    for topic in userdata['topics']:
        client.subscribe(topic)
        log.debug("Subscribed to %s", topic)

def on_message(client, userdata, msg):
    log.debug("Received message on %s", msg.topic)
    if msg.retain and userdata['ignore_retained']:
        log.debug("Ignoring retained message")
        return
    replies = None
    try:
        replies = userdata['callback'](msg.topic, msg.payload, **userdata['kwargs'])
    except Exception as e:
        log.error("Callback caused exception", exc_info = True)
    log.debug("Callback completed.")
    if replies is not None:
        replies = list(replies)
        log.debug("Received %s replies", len(replies))
        for reply in replies:
            try:
                topic, payload, retain = reply
            except ValueError:
                topic, payload = reply
                retain = False
            log.debug("Publishing '%s' to %s (retain: %s)", payload, topic, retain)
            client.publish(topic, payload, retain=retain)
            log.debug("Published '%s' to %s (retain: %s)", payload, topic, retain)

def mqtt_thread(client):
    client.loop_forever()

def run_script(callback, broker=None, topics=None, ignore_retained=False, blocking=True, **kwargs):
    if not broker:
        broker = os.environ['MQTT_BROKER']
    if not topics:
        topics = os.environ['MQTT_TOPICS'].split(",")

    userdata = {
        'topics': topics,
        'callback': callback,
        'ignore_retained': ignore_retained,
        'kwargs': kwargs
    }

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, userdata=userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    if "//"  in broker: # mqtt:// prefix is optional (NB mqtts:// is not supported)
        broker = broker.split("//")[1]
    client.connect(broker)
    if blocking:
        client.loop_forever()
    else:
        t = threading.Thread(target=mqtt_thread, args=(client,), daemon=True)
        t.start()
