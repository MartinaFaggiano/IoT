from MyMQTT import MQTT
import json 
import time
from urllib import request, parse
import requests


class CO_monitor():
    def __init__(self, broker, clientID, port, homeCatalog):
        self.mqtt = MQTT(broker, clientID, port, self)
        self.__message = json.load(open("dataFormat.json"))
        self.urlCatalog = homeCatalog 

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop

    def notify(self, topic, msg):
        payload = json.loads(msg.decode('utf-8'))
        for el in payload['e']:
            devName = topic.split('/')[-1]
            if el['v'] > 1000 and el['n'] == 'CO': 

                json_data = json.dumps({
                    "room" : devName,
                    "status" : "fail"
                })
                
                self.sendData(devName, topic+'/act', el["t"])

            else: 

                json_data = json.dumps({
                    "room" : topic.split('/')[-1],
                    "status" : "ok"
                })
                
            url = self.urlCatalog + '/postStatus'
            reqHome = requests.post(url, data = json_data)


    def sendData(self, deviceName, topic, time):
        message = self.__message
        message["bn"] = deviceName
        message["e"][0]["n"] = "Window"       
        message["e"][0]["v"] = "open" 
        message["e"][0]["t"] = time
        self.mqtt.publish(topic, message)

if __name__=="__main__": 
    conf = json.load(open("conf.json"))
    broker = conf.get('mqtt')['broker']
    portMQTT = conf.get('mqtt')['port']
    catalog = conf.get("rest")["HomeCatalog"]["ip"] + ":" + conf.get("rest")["HomeCatalog"]["port"]

    mon=CO_monitor(broker, "TempControl987", portMQTT, catalog)
    mon.start()


    while 1:
        params = {
        'rooms' : 'all',
        'sensor': 'co'}
        query_string = parse.urlencode( params ) 
        url = catalog + '/getDevices'
        url = url + "?" + query_string 

        reqTopic = request.urlopen(url)
        topics = reqTopic.read().decode('utf-8')
        topics = topics.replace('[', '')
        topics = topics.replace(']', '')
        topics = topics.replace('"', '')
        topics = topics.split(',')

        for top in topics: 
            mon.mqtt.subscribe(top)
        
        time.sleep(100)