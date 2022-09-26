from MyMQTT import MQTT
import json 
import time
from urllib import request, parse

class TimeShiftPUB():
    def __init__(self, broker, clientId, port):
        self.mqtt = MQTT(broker, clientId, port, self)
        self.__message=json.load(open("dataFormat.json"))
        self.messages  = []

    def start(self):
        self.mqtt.start()

    def stop(self):
        self.mqtt.stop()

    def sendData(self, deviceName, topic, time, turnOnOff):
        message = self.__message
        message["bn"] = deviceName
        message["e"][0]["n"] = "Schedule"       
        message["e"][0]["v"] = turnOnOff 
        message["e"][0]["t"] = time
        self.mqtt.publish(topic, message)
        print(message,'\n',topic)

    def ErrorType(self, e):
        if e == 400:
            print("Server error")


if __name__=="__main__": 
    conf = json.load(open("conf.json"))
    broker = conf.get('mqtt')['broker']
    portMQTT = conf.get('mqtt')['port']
    ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
    portCatalog = conf.get("rest")["HomeCatalog"]["port"]

    mon=TimeShiftPUB(broker, "TempControl1234", portMQTT)
    mon.start()

    
    flag = True
    starTime = time.mktime(time.localtime()) 

    while 1:
        actualTime = time.mktime(time.localtime())
        convert = time.strftime("%H:%M:%S", time.gmtime(actualTime+7200)) #convert actual time in hours

        if (actualTime - starTime > 600) or flag: #controllo ogni 10 minuti
            flag = False
            starTime = actualTime
            reqHome = request.urlopen(ipCatalog+ ':' +  portCatalog + '/getSchedules')
            dataHome = reqHome.read().decode('utf-8')
            schedules = json.loads(dataHome)

            for sched in schedules:         
                startHour = sched["startHour"]
                endHour = sched["endHour"]

                params = {
                'room' : sched["deviceName"],
                'sensor': 'temp'}
                query_string = parse.urlencode( params ) 
                url = ipCatalog+ ':' +  portCatalog + '/getDevices'
                url = url + "?" + query_string 

                reqTopic = request.urlopen(url)
                topic = reqTopic.read().decode('utf-8')
                topic = topic.replace('"', '')

                if convert >= startHour and convert <= endHour:
                    mon.sendData(sched["deviceName"], topic+'/act', convert, "on")

                    params = {
                        'room' : sched["deviceName"],
                        'status': 'on'}
                    query_string = parse.urlencode( params ) 
                    url = ipCatalog+ ':' +  portCatalog + '/getPower'
                    url = url + "?" + query_string 

                    reqHome = request.urlopen(url)  

                else :
                    mon.sendData(sched["deviceName"], topic+'/act', convert, "off")

                    params = {
                        'room' : sched["deviceName"],
                        'status': 'off'}
                    query_string = parse.urlencode( params ) 
                    url = ipCatalog+ ':' +  portCatalog + '/getPower'
                    url = url + "?" + query_string 

                    reqHome = request.urlopen(url)  


            