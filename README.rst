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

NB hbmqtt's reconnection handling does not resubscribe to topics upon
reconnection, and ``mqttwrapper`` does not yet work around this.

Examples
--------

- rxv2mqtt_
- tradfri-mqtt_

.. _rxv2mqtt: https://github.com/davea/rxv2mqtt/blob/master/main.py
.. _tradfri-mqtt: https://github.com/davea/tradfri-mqtt/blob/master/main.py
