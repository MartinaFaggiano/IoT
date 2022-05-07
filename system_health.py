from email import feedparser
from fileinput import filename
import urllib
from urllib import request
import json
from urllib.parse import urljoin
import cherrypy

from numpy import mean


# immagazzina in una variabile la risposta dal GET response
class health():
    #classe per richiamare thinkspeak
    
    def __init__(self) :
        self.threshold = 20 ##TODO prendere soglia aggiornata da Home Catalog per stanza 
        self.on_ = False #TODO recuperare status vero

    def evaluateMean(self, feeds):
        tempMedia = 0.0
        for i, temp in enumerate(feeds):
            tempMedia += float(temp["field1"])
        tempMedia = round(tempMedia/(i+1),2)
        return tempMedia

    def call_thinkspeak(self):
        
        reqHome = request.urlopen('http://127.0.0.1:8080/getDevicesFile')
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

  
    exposed = True
    def GET(self, *uri, **params):
        
        if len(params)==0 and len(uri)!=0:
            if uri[0] == 'getHealth':
                if self.on_:  
                    rooms = self.call_thinkspeak() 
                    for i, room in enumerate(rooms):
                        if int(room["meanTemperature"]) < self.threshold:
                            room["status"]= "Error" 
                        else:
                            room["status"]= "Ok" 
                    return json.dumps(rooms)
                else:
                    rooms = self.call_thinkspeak() 
                    for i, room in enumerate(rooms):
                        room["status"]= "OFF" 
                    return json.dumps(rooms)

    
  
if __name__=="__main__":

    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    
    cherrypy.config.update({'server.socket_port':8050})
    cherrypy.quickstart(health(), '/', conf)
