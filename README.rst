mqttwrapper
===========

A little glue package to make it simple to quickly put together scripts that
bridge MQTT and other libraries. See examples below.

Installation
------------

Install from PyPI::

  $ pip install mqttwrapper

``paho-mqtt`` is used as the underlying MQTT library.

Usage
-----

``mqttwrapper.run_script`` handles the setup/maintenance of the MQTT connection
and subscriptions to topics, and calls a callback function when messages are
received. It can run in blocking mode where it will take care of the MQTT
client handling or in non blocking mode where a new thread takes care this
leaving your main thread free for other things.

The simplest script looks something like this::

  from mqttwrapper import run_script

  def callback(topic, payload):
      print("Received payload {} on topic {}".format(payload, topic))

  def main():
      run_script(callback, broker="mqtt://127.0.0.1", topics=["my/awesome/topic1", "another/awesome/topic2"])

or in non blocking mode::

  def main():
      run_script(callback, broker="mqtt://127.0.0.1", topics=["my/awesome/topic1", "another/awesome/topic2"], blocking=False)
      while True:
          echo "Alive and kicking"
          time.sleep(1)

Any extra keyword arguments passed to ``run_script`` are passed back to the
callback function when it's called::

  from mqttwrapper import run_script

  def callback(topic, payload, context, foo):
      assert context == "hello"
      assert foo == "bar"
      print("Received payload {} on topic {}".format(payload, topic))

  def main():
      run_script(callback, broker="mqtt://127.0.0.1", topics=["my/awesome/topic1", "another/awesome/topic2"], context="hello", foo="bar")


If you don't need any context passed to your callback, just the topic and
payload of messages, you can run in 'importless' mode by creating a `callback`
module which has a `callback` function defined, then execute the
`mqttwrapper.run` module::

  $ cat callback.py
  def callback(topic, payload):
      print(topic, payload)
  
  $ python -m mqttwrapper.run

Retained messages
-----------------

You can ignore MQTT retained messages by passing ``ignore_retained=True`` when
calling ``run_script``.

Publishing messages from the callback
-------------------------------------

Sometimes your callback function might want to publish its own MQTT messages,
perhaps in reply to or an acknowledgement of a received message. This is
possible by returning an iterable of ``(topic, payload)`` tuples from the callback,
e.g.::

    def callback(topic, payload):
      print("Received payload {} on topic {}".format(payload, topic))
      return [
        ("{}/ack".format(topic), payload)
      ]


``mqttwrapper`` will take care of publishing these messages to the broker.

These tuples can optionally take the form ``(topic, payload, True)`` if you want
the published message to be marked as retained.

Configuration
-------------

``broker`` and ``topics`` can be omitted from the ``run_script`` call and
environment variables used instead:

- ``MQTT_BROKER``: MQTT broker to connect to, e.g. ``mqtt://127.0.0.1/``
- ``MQTT_TOPICS``: Comma-separated list of topics to subscribe to, e.g. ``my/topic1,my/topic2``


Examples
--------

- rxv2mqtt_

.. _rxv2mqtt: https://github.com/davea/rxv2mqtt/blob/master/main.py
