import os
import asyncio

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0

async def mqtt_loop(broker, topics, callback, **kwargs):
    client = MQTTClient()
    await client.connect(broker, cleansession=True)
    await client.subscribe([(topic, QOS_0) for topic in topics])
    try:
        while True:
            message = await client.deliver_message()
            packet = message.publish_packet
            topic = packet.variable_header.topic_name
            payload = bytes(packet.payload.data)
            callback(topic, payload, **kwargs)
    except ClientException:
        raise


def run_script(callback, broker=None, topics=None, **kwargs):
    if not broker:
        broker = os.environ['MQTT_BROKER']
    if not topics:
        topics = os.environ['MQTT_TOPICS'].split(",")

    asyncio.get_event_loop().run_until_complete(mqtt_loop(broker, topics, callback, **kwargs))
