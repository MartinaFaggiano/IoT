from MyMQTT import MQTT
import json 
import time
from urllib import request, parse
import orderdict

class Monitor():
    def __init__(self, broker, clientId, port):
        self.mqtt = MQTT(broker, clientId, port, self)
        self.messages = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop()

    def notify(self, topic, msg):
        payload = json.loads(msg.decode('utf-8'))
        self.messages.append(payload)
        print("Measurament\n %s" % payload)

if __name__ == "__main__":
    conf = json.load(open("conf2.json"))
    broker = conf.get("broker")
    port = conf.get("port")
    dev = conf.get("dev")


    mon = Monitor(broker, "87932489743298432980", port)
    mon.start()

    time.sleep(10)

    params = {'room':dev,
        'sensor':'temp'}
    query_string = parse.urlencode(orderdict.order(['room','sensor'], params)) 
    url = 'http://192.168.43.77:8080/getDevices'
    url = url + "?" + query_string
    print(url)

    reqTopic = request.urlopen(url)
    topics = reqTopic.read().decode('utf-8')
    top = topics.replace('"', '')

    mon.mqtt.subscribe(top+'/act')


    while 1: 
        time.sleep(1)

    mon.stop()