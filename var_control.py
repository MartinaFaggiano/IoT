from concurrent.futures import thread
from threading import Thread
from MyMQTT import MQTT
import json 
import time
from urllib import request, parse
import threading


class Temp_monitor(threading.Thread):
    def __init__(self, broker, clientID, port):
        self.mqtt = MQTT(broker, clientID, port, self)
        self.messages = []

        conf = json.load(open("conf.json"))        
        self.ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
        self.portCatalog = conf.get("rest")["HomeCatalog"]["port"]

        # self.ipHealth = conf.get("rest")["Health"]["ip"]
        # self.portHealth = conf.get("rest")["Health"]["port"]

        # self.ipEnv = conf.get("rest")["Env"]["ip"]
        # self.portEnv = conf.get("rest")["Env"]["port"]

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop

    def notify(self, topic, msg): #TODO
        payload = json.loads(msg)
        if payload['e']['v'] > 1000: 

            reqHome = request.urlopen(self.ipCatalog+ ':' +  self.portCatalog + '/getStatusFile')
            dataHome = reqHome.read().decode('utf-8')
            filename_ = json.loads(dataHome)
            data = json.load(open(filename_["filename"]))

            #check status Temp
            for dev in data["devicesList"]:
                if topic.split('/')[-1] == dev['deviceName']:
                    dev["status"] = 'fail'
            with open(filename_["filename"], "w") as file:
                    json.dump(data, file)

            #serve per mandare il messaggio di apertura finestre al rasp.
            self._paho_mqtt.publish(topic+'/act', json.dumps(msg), 2)

            self.messages.append(payload)
             

    def sendData(self, deviceName, topic, time, turnOnOff):
        message = self.__message
        message["bn"] = deviceName
        message["e"][0]["n"] = "Schedule"       
        message["e"][0]["v"] = turnOnOff 
        message["e"][0]["t"] = time
        self.mqtt.publish(topic, message)  


if __name__=="__main__":
    conf = json.load(open("conf.json"))
    broker = conf.get('mqtt')['broker']
    portMQTT = conf.get('mqtt')['port']

    ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
    portCatalog = conf.get("rest")["HomeCatalog"]["port"]

    tm_mon=Temp_monitor(broker, "TempControl", portMQTT)
    tm_mon.start()


    flag = True
    starTime = time.mktime(time.localtime)
    while 1:
        actualTime = time.mktime(time.localtime())
        convert = time.strftime("%H:%M:%S", time.gmtime(actualTime+7200)) #convert actual time in hours
        if (actualTime - starTime > 5) or flag: #controllo ogni 5 minuti
            params = {
            'rooms' : 'all',
            'sensor': 'temp'}
            query_string = parse.urlencode( params ) 
            url = ipCatalog+ ':' +  portCatalog + '/getDevices'
            url = url + "?" + query_string 

            reqTopic = request.urlopen(url)
            topics = reqTopic.read().decode('utf-8')
            topics = topics.replace('[', '')
            topics = topics.replace(']', '')
            topics = topics.replace('"', '')
            topics = topics.split(',')

            for top in topics: 
                tm_mon.mqtt.subscribe(top)
        
        time.sleep(300)


