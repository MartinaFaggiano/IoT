from MyMQTT import MQTT
import json 
import time
from urllib import request, parse


class Temp_monitor():
    def __init__(self, broker, clientID, port):
        self.mqtt = MQTT(broker, clientID, port, self)
        self.messages = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop

    def notify(self, topic, msg):
        payload = json.loads(msg)
        if payload['e']['v'] > 1000:  #modificare valore, soglia per stanza  

            reqHome = request.urlopen('http://127.0.0.1:8080/getStatusFile')
            dataHome = reqHome.read().decode('utf-8')
            filename_ = json.loads(dataHome)
            data = json.load(open(filename_["filename"]))

            #check status Temp
            for dev in data["devicesList"]:
                if topic.split('/')[-1] == dev['deviceName']:
                    dev["status"] = 'fail'
            with open(filename_["filename"], "w") as file:
                    json.dump(data, file)

            #serve per mandare il messaggio di apertura finestre al rasp. TODO lato rasp subscriber
            self._paho_mqtt.publish(topic+'/act', json.dumps(msg), 2)

            self.messages.append(payload)
             
        hist = payload['e']['v']
        # print(f"Registered measure: \n {payload}")

    def sendData(self, deviceName, topic, time, turnOnOff):
        message = self.__message
        message["bn"] = deviceName
        message["e"][0]["n"] = "Schedule"       
        message["e"][0]["v"] = turnOnOff 
        message["e"][0]["t"] = time
        self.mqtt.publish(topic, message)  

if __name__=="__main__":
    conf = json.load(open("conf.json"))
    broker = conf.get("broker")
    port = conf.get("port")

    co_mon=Temp_monitor(broker, "TempControl", port)
    co_mon.start()


    flag = True
    starTime = time.mktime(time.localtime()) 
    while (1) :
        actualTime = time.mktime(time.localtime())
        convert = time.strftime("%H:%M:%S", time.gmtime(actualTime+7200)) #convert actual time in hours

        #iscrizione ai topic di tutte le stanze
        if (actualTime - starTime > 5) or flag: #controllo ogni 5 minuti
            params = {
            'rooms' : 'all',
            'sensor': 'temp'}
            query_string = parse.urlencode( params ) 
            url = 'http://127.0.0.1:8080/getDevices'
            url = url + "?" + query_string 

            reqTopic = request.urlopen(url)
            topics = reqTopic.read().decode('utf-8')
        
            for top in topics: 
                co_mon.mqtt.subcribe(top)

                #TODO gestire pubblicazioni su questo topic lato rasp

    

    co_mon.stop()