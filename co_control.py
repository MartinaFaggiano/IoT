from MyMQTT import MQTT
import json 
import time

class Schermo():
    def __init__(self, broker, clientID, port):
        self.mqtt = MQTT(broker, clientID, port, self)
        self.messages = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop

    def notify(self, topic, msg):
        payload = json.loads(msg)
        print(f"Registered measure: \n {payload}")
        self.messages.append(payload)
        

if __name__=="__main__":
    conf = json.load(open("config.json"))
    broker = conf.get("broker")
    port = conf.get("port")
    topic = conf.get("topic") 

    sc=Schermo(broker, "Martina", port)
    sc.start()
    sc.mqtt.subcribe(topic)

    start = time.time()
    while (time.time()-start) < 60:
        time.sleep(3)
    with open("temp_log.json", "w") as file:
        json.dump(sc.messages, file)
    sc.stop()