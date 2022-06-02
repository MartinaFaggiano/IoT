import re

import urllib
from MyMQTT import MQTT
import json 
import time
import requests
from urllib import request
import os 

class TimeShiftPUB():
    def __init__(self, broker, clientId, port):
        self.mqtt = MQTT(broker, clientId, port, self)
        self.__message=json.load(open("dataFormat.json"))
        self.messages  = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop()

    def notify(self, topic, msg):
        payload = json.loads(msg)
        self.messages.append(payload)
        print("Measurament\n %s" % payload)

        #TODO controllo misurazioni con soglia 


    def sendData(self, deviceName, topic, time, turnOnOff):
        message = self.__message
        message["bn"] = deviceName
        message["e"][0]["n"] = "Schedule"       
        message["e"][0]["v"] = turnOnOff 
        message["e"][0]["t"] = time
        self.mqtt.publish(topic, message)

    def ErrorType(self, e):
        if e == 400:
            print("Server error")
            

if __name__ == "__main__":
    conf = json.load(open("conf.json"))
    broker = conf.get("broker")
    port = conf.get("port")
    mon = TimeShiftPUB(broker, "87932489743298432980", port)
    mon.start()


    flag = True
    starTime = time.mktime(time.localtime()) 

    while (1):
        
        actualTime = time.mktime(time.localtime())
        convert = time.strftime("%H:%M:%S", time.gmtime(actualTime+7200)) #convert actual time in hours

        if (actualTime - starTime > 10) or flag: #controllo ogni 10 minuti
            flag = False
            starTime = actualTime
            reqHome = request.urlopen('http://127.0.0.1:8080/getSchedules')
            dataHome = reqHome.read().decode('utf-8')
            schedules = json.loads(dataHome)

            for sched in schedules:         
                startHour = sched["startHour"]
                endHour = sched["endHour"]

                params = {
                'room' : sched["deviceName"]}
                query_string = urllib.parse.urlencode( params ) 
                url = 'http://127.0.0.1:8080/getDevices'
                url = url + "?" + query_string 

                if convert >= startHour and convert <= endHour:
                    reqTopic = request.urlopen(url)
                    topic = reqTopic.read().decode('utf-8')
                    mon.mqtt.subscribe(topic)
                    mon.sendData(sched["deviceName"], topic, convert, "on")

                else :
                    reqTopic = request.urlopen(url)
                    topic = reqTopic.read().decode('utf-8')
                    mon.mqtt.subscribe(topic)
                    mon.sendData(sched["deviceName"], topic, convert, "off")

    
    mon.stop()  

    #TODO controllo temperatura --> accendi spegni  -- publisher     #è da fare da un altra parte
    #TODO riceve misurazioni temperatura -- subscriber               #legato alla riga sopra 

    #TODO tramite REST -- set the desired temperature of the room in the Home Catalog     # gestito da telegram 
    # PERCHè DOVREBBE CAMBIARE LA TEMPERATURA?

