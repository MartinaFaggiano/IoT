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

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop

    def notify(self, topic, msg):
        payload = json.loads(msg)
        #check Temp
        for el in payload['e']:
            if el['v'] < 15: 
                devName = topic.split('/')[-1]
                params = {
                    'room' : devName}
                query_string = parse.urlencode( params ) 
                url = self.ipCatalog+ ':' +  self.portCatalog + '/getSchedules'
                url = url + "?" + query_string 

                reqHome = request.urlopen(url)
                dataHome = reqHome.read().decode('utf-8')
                data_dictHome = json.loads(dataHome)

                #check schedule
                actualTime = time.mktime(time.localtime())
                convert = time.strftime("%H:%M:%S", time.gmtime(actualTime+7200))
                if data_dictHome[0]['startHour']> convert and data_dictHome[0]['endHour'] < convert:  
                    params = {
                        'room' : devName,
                        'status': 'on'}
                    query_string = parse.urlencode( params ) 
                    url = self.ipCatalog+ ':' +  self.portCatalog + '/getPower'
                    url = url + "?" + query_string 

                    reqHome = request.urlopen(url)

                    #messaggio di accensione riscaldamento al rasp.
                    self.sendData(devName, topic+'/act', convert, "on")
             

    def sendData(self, deviceName, topic, time, turnOnOff):
        message = self.__message
        message["bn"] = deviceName
        message["e"][0]["n"] = "Schedule"       
        message["e"][0]["v"] = turnOnOff 
        message["e"][0]["t"] = time
        self.mqtt.publish(topic, message)  
        print(message)


if __name__=="__main__":
    conf = json.load(open("conf.json"))
    broker = conf.get('mqtt')['broker']
    portMQTT = conf.get('mqtt')['port']

    ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
    portCatalog = conf.get("rest")["HomeCatalog"]["port"]

    tm_mon=Temp_monitor(broker, "TempControl", portMQTT)
    tm_mon.start()

    flag = True
    starTime = time.mktime(time.localtime())
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


