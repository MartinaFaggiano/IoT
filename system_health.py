from email import feedparser
from fileinput import filename
import urllib
from urllib import request
import json
from urllib.parse import urljoin
import cherrypy

from numpy import mean, power



class Health():
    #classe per richiamare thinkspeak
    
    def __init__(self) :
        pass

    def evaluateMean(self, feeds):
        tempMedia = 0.0
        cnt = 0
        for i, temp in enumerate(feeds):
            tempMedia += float(temp["field1"])
            cnt += 1
        tempMedia = round(tempMedia/(cnt),2)
        return tempMedia

    def call_thinkspeak(self):
        
        reqHome = request.urlopen('http://192.168.43.77:8080/getDevicesFile')
        dataHome = reqHome.read().decode('utf-8')
        filename_ = json.loads(dataHome)
        data = json.load(open(filename_["filename"]))

        urlJsons = []
        for dev in data["devicesList"]:
                urlJsons.append({
                    "deviceName":dev["deviceName"],
                    "channel": dev["channel"]
                })

        temp = []
        for i, ch in enumerate(urlJsons):
            response = request.urlopen(ch["channel"])

            # preleva i dati json dalla richiesta
            data = response.read().decode('utf-8')

            # convertiamo la stringa in dizionario
            data_dict = json.loads(data)

            #separiamo i valori che ci interessano
            feeds = data_dict['feeds']
            temp.append({
                    "deviceName":ch["deviceName"],
                    "meanTemperature": self.evaluateMean(feeds),
                    "status": ""
                })
        
        return temp
    
    def power_OnOff(self):
        powerList = []
        reqHome = request.urlopen('http://192.168.43.77:8080/getStatusFile')
        dataHome = reqHome.read().decode('utf-8')
        filename_ = json.loads(dataHome)
        data = json.load(open(filename_["filename"]))

        for e in data['devicesList']:
            powerList.append({e['deviceName']: e['power']})
        return powerList

        
    exposed = True
    def GET(self, *uri, **params):
        
        reqHome = request.urlopen('http://192.168.43.77:8080/getThreshold')
        dataHome = reqHome.read().decode('utf-8')
        lista_threshold = json.loads(dataHome)
        powerList = self.power_OnOff()
        powerJson = json.dumps(powerList)

        if len(params)==0 and len(uri)!=0:
            if uri[0] == 'getHealth':
                rooms = self.call_thinkspeak() 
                for i, room in enumerate(rooms): #cicla sulle room di teamspeak
                    for j, rth in enumerate(lista_threshold):  #cicla sulle schedule 
                        if room["deviceName"] == rth["deviceName"]:
                            for e in powerList:
                                powerJson = json.dumps(e)
                                if 'on' in powerJson:

                                    if int(room["meanTemperature"]) < int(rth["th_sup"]):
                                        room["status"]= "Check the system" 
                                    else:
                                        room["status"]= "Ok" 
                                else:
                                    rooms = self.call_thinkspeak() 
                                    for i, room in enumerate(rooms):
                                        room["status"]= "OFF" 
                return json.dumps(rooms)
                
        
if __name__=="__main__":
    # def run(self):

        conf={
            '/':{
                'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on' : True
            }
        }
        
        cherrypy.config.update({'server.socket_port':8050})
        cherrypy.quickstart(Health(), '/', conf)