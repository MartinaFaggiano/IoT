from MyMQTT import MQTT
import json 
import time

class Monitor():
    def __init__(self, broker, clientId, port):
        self.mqtt = MQTT(broker, clientId, port, self)
        self.messages = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop()

    def notify(self, topic, msg):
        payload = json.loads(msg)
        self.messages.append(payload)
        print("Measurament\n %s" % payload)

if __name__ == "__main__":
    conf = json.load(open("conf.json"))
    broker = conf.get("broker")
    port = conf.get("port")
    topic = conf.get("topic")

    mon = Monitor(broker, "87932489743298432980", port)
    mon.start()
    mon.mqtt.subscribe(topic)

    starTime = time.time()
    while (time.time()-starTime) < 60 :
        time.sleep(1)

    with open("hr_log.json", "w") as file:
        json.dump(mon.messages, file)

    mon.stop()