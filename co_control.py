from MyMQTT import MQTT
import json 
import time
from urllib import request, parse


class CO_monitor():
    def __init__(self, broker, clientID, port):
        self.mqtt = MQTT(broker, clientID, port, self)
        self.messages = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop

    def notify(self, topic, msg):
        payload = json.loads(msg)
        if payload > qualcosa: 
            #TODO cambia valore stringa alarm in devides.json seguendo il topic come variabile per la stanza
            # manda messaggio di notifica del problema 
            self.messages.append(payload)
             

        # print(f"Registered measure: \n {payload}")
        self.messages.append(payload)
        

if __name__=="__main__":
    conf = json.load(open("conf.json"))
    broker = conf.get("broker")
    port = conf.get("port")

    co_mon=CO_monitor(broker, "CoControl", port)
    co_mon.start()


    flag = True
    starTime = time.mktime(time.localtime()) 
    while (1) :
        actualTime = time.mktime(time.localtime())
        convert = time.strftime("%H:%M:%S", time.gmtime(actualTime+7200)) #convert actual time in hours

        if (actualTime - starTime > 5) or flag: #controllo ogni 5 minuti
            params = {
            'rooms' : 'all',
            'sensor': 'co'}
            query_string = parse.urlencode( params ) 
            url = 'http://127.0.0.1:8080/getDevices'
            url = url + "?" + query_string 

            reqTopic = request.urlopen(url)
            topics = reqTopic.read().decode('utf-8')
        
        for top in topics: 
            co_mon.mqtt.subcribe(top)

    

    co_mon.stop()