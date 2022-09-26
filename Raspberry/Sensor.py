from MyMQTT import MQTT
import json
import time
import ReadSens as sens
from urllib import parse, request
import orderdict

class Sensor():
    def __init__(self, broker, clientID, port):
        self.mqtt = MQTT(broker, clientID, port, None)
        self.__message = json.load(open("dataFormat.json"))

    def run(self):
        self.mqtt.start()
    
    def end(self):
        self.mqtt.stop()

    def sendData(self, topic, time, temp = None, co = None, hum = None):
        message = self.__message
        message["bn"] = "RoomSystem_1"
	
        if temp != None:
                 message["e"][0]["n"] = 'temperature'
                 message["e"][0]["v"] = temp
                 message["e"][0]["t"] = time
        else: 
                 message["e"].pop(0)            
        if co != None:
                message["e"].append({"n": 'CO', "v": co/100 - 10, "t" : time})
        if hum != None:        
                message["e"].append({"n": 'humidity', "v": hum, "t" : time})
        #print(message)

        self.mqtt.publish(topic, message)

if __name__ == "__main__":
    conf = json.load(open("conf.json"))
    broker = conf.get("broker")
    port = conf.get("port")
    topic = conf.get("topic")

    sn = Sensor(broker, "KDEZIRg5NyMxMB4bDx8dEQo", port)
    sn.run()

    conf2 = json.load(open("conf2.json"))
    broker2 = conf2.get("broker")
    port2 = conf2.get("port")
    dev = conf2.get("dev")

    sn2 = Sensor(broker2, "879324897432984322", port2)
    sn2.run()

    params = {'room':dev,
        'sensor':'temp'}
    query_string = parse.urlencode(orderdict.order(['room','sensor'], params)) 
    url = 'http://192.168.43.77:8080/getDevices'
    url = url + "?" + query_string

    reqTopic = request.urlopen(url)
    topics = reqTopic.read().decode('utf-8')
    top_temp = topics.replace('"', '')

    params = {'room':dev,
        'sensor':'co'}
    query_string = parse.urlencode(orderdict.order(['room','sensor'], params)) 
    url = 'http://192.168.43.77:8080/getDevices'
    url = url + "?" + query_string

    reqTopic = request.urlopen(url)
    topics = reqTopic.read().decode('utf-8')
    top_co = topics.replace('"', '')

    #humidity
    params = {'room':dev,
        'sensor':'hum'}
    query_string = parse.urlencode(orderdict.order(['room','sensor'], params)) 
    url = 'http://192.168.43.77:8080/getDevices'
    url = url + "?" + query_string

    reqTopic = request.urlopen(url)
    topics = reqTopic.read().decode('utf-8')
    top_hum = topics.replace('"', '')

    while 1: 
        mis =  time.time()
        temp, co, hum = sens.measure()
        if hum > 100:
	    #corregge il malfunzionamento di una sonda
            hum = hum_storico
        sn.sendData(topic, mis, temp, co, hum)
        sn2.sendData(top_temp, mis, round(temp,1))
        sn2.sendData(top_co, mis,None, round(co,1), None)
        sn2.sendData(top_hum, mis, None, None, round(hum,1))
        hum_storico = hum 
        time.sleep(10)
    sn.end()
    sn2.end()



