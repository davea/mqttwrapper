import os
import asyncio

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0

async def mqtt_loop(broker, topics, callback, context_callback, **kwargs):
    if context_callback is not None:
        kwargs.update(await context_callback())
    client = MQTTClient()
    await client.connect(broker, cleansession=True)
    await client.subscribe([(topic, QOS_0) for topic in topics])
    try:
        while True:
            message = await client.deliver_message()
            packet = message.publish_packet
            topic = packet.variable_header.topic_name
            payload = bytes(packet.payload.data)
            replies = await callback(topic, payload, **kwargs)
            if replies is not None:
                for reply_topic, reply_payload in replies:
                    await client.publish(reply_topic, reply_payload)
    except ClientException:
        raise


def run_script(callback, broker=None, topics=None, context_callback=None, **kwargs):
    if not broker:
        broker = os.environ['MQTT_BROKER']
    if not topics:
        topics = os.environ['MQTT_TOPICS'].split(",")

    asyncio.get_event_loop().run_until_complete(mqtt_loop(broker, topics, callback, context_callback, **kwargs))
