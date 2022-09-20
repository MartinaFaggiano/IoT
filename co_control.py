from MyMQTT import MQTT
import json 
import time
from urllib import request, parse


class CO_monitor():
    def __init__(self, broker, clientID, port, homeCatalog):
        self.mqtt = MQTT(broker, clientID, port, self)
        self.messages = []
        self.urlCatalog = homeCatalog 

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop

    def notify(self, topic, msg):
        payload = json.loads(msg)
        if payload['e']['v'] > 1000: 

            reqHome = request.urlopen(self.urlCatalog+'/getStatusFile')
            dataHome = reqHome.read().decode('utf-8')
            filename_ = json.loads(dataHome)
            data = json.load(open(filename_["filename"]))

            #check status CO
            for dev in data["devicesList"]: #TODO controllare che faccia la modifica al file
                if topic.split('/')[-1] == dev['deviceName']:
                    dev["status"] = 'fail'
                    self.sendData(dev['deviceName'], topic+'/act', msg["e"][0]["t"], 2)
            with open(filename_["filename"], "w") as file:
                    json.dump(data, file)

            # self.messages.append(payload)

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