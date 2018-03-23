mqttwrapper
===========

A little glue package to make it simple to quickly put together scripts that
bridge MQTT and other libraries. See examples below.

Installation
------------

Install from PyPI::

  $ pip install mqttwrapper

By default ``paho-mqtt`` will be used as the MQTT library, but you can use
``hbmqtt`` if you wish - see below. To install, use::

  $ pip install mqttwrapper[hbmqtt]

Usage
-----

``mqttwrapper.run_script`` handles the setup/maintenance of the MQTT connection
and subscriptions to topics, and calls a callback function when messages are
received.

The simplest script looks something like this::

  from mqttwrapper import run_script

  def callback(topic, payload):
      print("Received payload {} on topic {}".format(payload, topic))

  def main():
      run_script(callback, broker="mqtt://127.0.0.1", topics=["my/awesome/topic1", "another/awesome/topic2"])

Any extra keyword arguments passed to ``run_script`` are passed back to the
callback function when it's called::

  from mqttwrapper import run_script

  def callback(topic, payload, context, foo):
      assert context == "hello"
      assert foo == "bar"
      print("Received payload {} on topic {}".format(payload, topic))

  def main():
      run_script(callback, broker="mqtt://127.0.0.1", topics=["my/awesome/topic1", "another/awesome/topic2"], context="hello", foo="bar")

Publishing messages from the callback
-------------------------------------

Sometimes your callback function might want to publish its own MQTT messages,
perhaps in reply to or an acknowledgement of a received message. This is
possible by returning a list of ``(topic, payload)`` tuples from the callback,
e.g.::

    def callback(topic, payload):
      print("Received payload {} on topic {}".format(payload, topic))
      return [
        ("{}/ack".format(topic), payload)
      ]


``mqttwrapper`` will take care of publishing these messages to the broker.

Configuration
-------------

``broker`` and ``topics`` can be omitted from the ``run_script`` call and
environment variables used instead:

- ``MQTT_BROKER``: MQTT broker to connect to, e.g. ``mqtt://127.0.0.1/``
- ``MQTT_TOPICS``: Comma-separated list of topics to subscribe to, e.g. ``my/topic1,my/topic2``

asyncio/hbmqtt
--------------

The asyncio-powered ``hbmqtt`` MQTT library can be used instead, if you like::

  from mqttwrapper.hbmqtt_backend import run_script

  async def callback(topic, payload):
      print("Received payload {} on topic {}".format(payload, topic))


Note that your callback must be an awaitable in this case.

Your callback may require context arguments which themselves are async objects
or awaitables which poses a challenge: how to set these up outside of an asyncio
event loop before calling ``run_script``? In this case, you can pass a
``context_callback`` awaitable as a kwarg to ``run_script``. This is run at the
start of the MQTT loop, and should return a dict which will be merged into the
kwargs which are passed to your callback. For example::

  from mqttwrapper.hbmqtt_backend import run_script

  async def setup_db():
    return {
      "query_db": query_db
    }

  async def query_db(value):
    # pretend this is some slow DB query, for example.
    await asyncio.sleep(3)
    return value * 2

  async def callback(topic, payload, query_db):
      db_result = await query_db(int(payload))
      print("Received payload {} on topic {}, db result: {}".format(payload, topic, db_result))

  def main():
      run_script(callback, context_callback=setup_db)


NB hbmqtt's reconnection handling does not resubscribe to topics upon
reconnection, and ``mqttwrapper`` does not yet work around this.

Examples
--------

- rxv2mqtt_
- tradfri-mqtt_ (uses asyncio)

.. _rxv2mqtt: https://github.com/davea/rxv2mqtt/blob/master/main.py
.. _tradfri-mqtt: https://github.com/davea/tradfri-mqtt/blob/master/main.py
