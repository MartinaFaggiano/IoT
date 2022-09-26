import paho.mqtt.client as PahoMQTT
import json

class MQTT():
    def __init__(self, broker, clientID, port, notifier):
        self.broker = broker
        self.clientID = clientID
        self.port = port
        self.notifier = notifier

        self._topic = ""

        self._isSubscriber = False
        self._paho_mqtt=PahoMQTT.Client(clientID, True)

        #devo definire i due callback 
        self._paho_mqtt.on_connect = self.myOnConnect 
        self._paho_mqtt.on_message = self.myOnMessage

    def start(self):
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        if(self._isSubscriber):
            self._paho_mqtt.unsubscribe(self._topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def subscribe(self, topic):
        self._isSubscriber = True
        self._topic = topic
        self._paho_mqtt.subscribe(topic, 2)
        print("subscribed to %s" % (topic))

    def unsubscribe(self, topic):
        if(self.isSubscriber):
            self._paho_mqtt.unsubscribe(self._topic)

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s, with this code: %d" % (self.broker, rc))

    def myOnMessage (self, paho_mqtt , userdata, msg):
        self.notifier.notify(msg.topic, msg.payload)

    def publish(self, topic, msg):
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)


    