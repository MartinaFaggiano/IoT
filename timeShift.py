from MyMQTT import MQTT
import json 
import time
import requests

class Monitor():
    def __init__(self, broker, clientId, port):
        self.mqtt = MQTT(broker, clientId, port, self)
        self.messages = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop()

    def notify(self, topic, msg):
        payload = json.loads(msg)
        self.messages.append(payload)
        print("Measurament\n %s" % payload)

        #TODO controllo misurazioni con soglia 

#aggiunto per mandare i dati sull'accendi spegni 
    def sendData(self, topic, time, sens):
        message = self.__message
        message["bn"] = "Sensor1"
        message["e"][0]["v"] = sens
        message["e"][0]["t"] = time
        self.mqtt.publish(topic, message)

    def ErrorType(self, e):
        if e == 400:
            print("Server error")

if __name__ == "__main__":
    conf = json.load(open("conf.json"))
    sched = json.load(open("schedule.json"))
    top = json.load(open("MQTT-topics.json"))

    broker = conf.get("broker")
    port = conf.get("port")
    topic = top.get("topic").Schedule.heating

    mon = Monitor(broker, "87932489743298432980", port)
    mon.start()
    mon.mqtt.subscribe(topic)

    starTime = time.time()
    while (1):
        #TODO controllo orario --> accendi spegni -- publisher

        #TODO controllo temperatura --> accendi spegni  -- publisher 

        #TODO riceve misurazioni temperatura -- subscriber 

        #TODO tramite REST -- set the desired temperature of the room in the Home Catalog
        # PERCHè DOVREBBE CAMBIARE LA TEMPERATURA?
        #per fare le richieste post -- modificare il json
        try:
            r = requests.post('http://localhost/post/schedule', json={"key": "value"})

            raise mon.ErrorType("Error message")
        except mon.ErrorType as e: #code to run if error occurs
            print("Temperatura non impostata")
            #code to run if error is raised
        else: 
            pass

        time.sleep(1)

    mon.stop()