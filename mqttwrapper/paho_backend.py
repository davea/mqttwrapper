import logging
import os
import threading
from urllib.parse import urlsplit

import paho.mqtt.client as mqtt

log = logging.getLogger("mqttwrapper.paho_backend")

def on_connect(client, userdata, flags, rc):
    log.debug("Connected")
    for topic in userdata['topics']:
        client.subscribe(topic, qos=userdata['qos'])
        log.debug("Subscribed to %s", topic)

def on_disconnect(client, userdata, rc):
    if rc != mqtt.MQTT_ERR_SUCCESS:
        log.warning("Lost broker connection (%s), reconnecting",
                    mqtt.error_string(rc))

def on_message(client, userdata, msg):
    log.debug("Received message on %s", msg.topic)
    if msg.retain and userdata['ignore_retained']:
        log.debug("Ignoring retained message")
        return
    replies = None
    try:
        replies = userdata['callback'](msg.topic, msg.payload, **userdata['kwargs'])
    except Exception:
        if userdata['raise_exceptions']:
            raise
        log.exception("Callback caused exception")
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

def parse_broker(broker):
    if "//" not in broker:
        broker = "mqtt://" + broker
    url = urlsplit(broker)
    if url.scheme not in ("mqtt", "mqtts"):
        raise ValueError(f"Unsupported broker URL scheme: {url.scheme}")
    tls = url.scheme == "mqtts"
    port = url.port or (8883 if tls else 1883)
    return url.hostname, port, tls, url.username, url.password

def mqtt_thread(client):
    client.loop_forever()

def run_script(callback, broker=None, topics=None, ignore_retained=False, blocking=True,
               client_id="", clean_session=True, qos=0, raise_exceptions=False, **kwargs):
    if not broker:
        broker = os.environ['MQTT_BROKER']
    if not topics:
        topics = os.environ['MQTT_TOPICS'].split(",")
    if not clean_session and not client_id:
        raise ValueError("client_id is required when using clean_session")
    if raise_exceptions and not blocking:
        raise ValueError("raise_exceptions can't be used with blocking=False")

    userdata = {
        'topics': topics,
        'qos': qos,
        'callback': callback,
        'ignore_retained': ignore_retained,
        'raise_exceptions': raise_exceptions,
        'kwargs': kwargs
    }

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION1,
        client_id=client_id,
        clean_session=clean_session,
        userdata=userdata,
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    host, port, tls, username, password = parse_broker(broker)
    if tls:
        client.tls_set()
    if username:
        client.username_pw_set(username, password)
    client.connect(host, port)
    if blocking:
        client.loop_forever()
    else:
        t = threading.Thread(target=mqtt_thread, args=(client,), daemon=True)
        t.start()
