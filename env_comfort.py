from email import feedparser
from fileinput import filename
import urllib
from urllib import request
import json
from urllib.parse import urljoin
import cherrypy




# immagazzina in una variabile la risposta dal GET response
class Environmental():
    #classe per richiamare thinkspeak
    
    def __init__(self) :
        self.threshold = 20
        conf = json.load(open("conf.json"))

        self.ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
        self.portCatalog = conf.get("rest")["HomeCatalog"]["port"]


 
    def call_thinkspeak(self, room):

        reqHome = request.urlopen(self.ipCatalog+ ':' +  self.portCatalog + '/getDevicesFile')
        dataHome = reqHome.read().decode('utf-8')
        filename_ = json.loads(dataHome)
        data = json.load(open(filename_["filename"]))

        for dev in data["devicesList"]:
            if dev["deviceName"] == room:
                urlJson = dev["channel"]

        response = request.urlopen(urlJson)
        data = response.read().decode('utf-8')
        data_dict = json.loads(data)
        feeds = data_dict['feeds']
        
        return feeds

    exposed = True
    def GET(self, *uri, **params):

        if len(params)!=0 and len(uri)!=0:
            chiave = list(params.keys())[0]
            if chiave == "room":
                if uri[0] == 'getComfort':
                    
                    feeds = self.call_thinkspeak(params["room"]) 
                    temp =  float(feeds[-1]['field1'])
                    hum =  float(feeds[-1]['field2'])
                    co =  float(feeds[-1]['field3'])

                    if temp > self.threshold and temp < 23:
                        if hum < 60 and hum > 20: 
                            return "Temperature:"+ str(temp) + '\nHumidity:'+ str(hum) + '\nOptimal comfort'
                        else:
                            return "Temperature:"+ str(temp) + '\nHumidity:'+ str(hum) + '\nHumidity level too high'

                    elif temp < self.threshold and str(temp) > 18:
                        if hum > 60 : 
                            return "Temperature:"+ str(temp) + '\n"Humidity:'+ str(hum) + '\nOptimal comfort'
                        else:
                            return "Temperature:"+ str(temp) + '\n"Humidity:'+ str(hum) + '\nHumidity level too low'
                    
                    if co > 1000:
                        return "Co level:"+ str(co) + ' ppm' + "\nDangerous quantity, OPEN THE WINDOWS!"  
            elif chiave == "all":        
                if uri[0] == 'getCOstatus':

                    #richiede alla home catalog il file di status
                    reqHome = request.urlopen(self.ipCatalog+ ':' +  self.portCatalog + '/getStatusFile')
                    dataHome = reqHome.read().decode('utf-8')
                    filename_ = json.loads(dataHome)
                    data = json.load(open(filename_["filename"]))

                    #check status CO #TODO sistemare chiamata per stanze dell'utente
                    for dev in data["devicesList"]:
                        statusCO = dev["statusCO"]
                        if statusCO == 'fail':
                            return 'CO level out of range in ' + dev['deviceName']

                    return 'False'


if __name__=="__main__":
    # def run(self):
        conf={
            '/':{
                'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on' : True
            }
        }
        
        cherrypy.config.update({'server.socket_port':8070})
        cherrypy.quickstart(Environmental(), '/', conf)