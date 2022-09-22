from email import feedparser
from fileinput import filename
import urllib
from urllib import request
import json
from urllib.parse import urljoin
import cherrypy

from numpy import mean, power



class Health():
    
    def __init__(self) :
        conf = json.load(open("conf.json"))

        self.ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
        self.portCatalog = conf.get("rest")["HomeCatalog"]["port"]

    def evaluateMean(self, feeds):
        tempMedia = 0.0
        cnt = 0
        for i, temp in enumerate(feeds):
            if temp["field1"] != None: 
                tempMedia += float(temp["field1"])
                cnt += 1
        tempMedia = round(tempMedia/(cnt),2)
        return tempMedia

    #classe per richiamare thinkspeak
    def call_thinkspeak(self, chatid):
        params = {
            'chatid' : chatid}

        query_string = urllib.parse.urlencode( params ) 
        url = self.ipCatalog+ ':' +  self.portCatalog + '/getDevicesList'
        url = url + "?" + query_string 
        reqHome = request.urlopen(url)
        dataHome = reqHome.read().decode('utf-8')
        data = json.loads(dataHome)

        urlJsons = []
        for dev in data:
                urlJsons.append({
                    "deviceName":dev["deviceName"],
                    "channel": dev["channel"]
                })

        temp = []
        for i, ch in enumerate(urlJsons):
            response = request.urlopen(ch["channel"])
            data = response.read().decode('utf-8')
            data_dict = json.loads(data)
            feeds = data_dict['feeds']

            temp.append({
                    "deviceName":ch["deviceName"],
                    "meanTemperature": self.evaluateMean(feeds),
                    "status": ""
                })
        
        return temp
    
    def power_OnOff(self):
        powerList = []
        reqHome = request.urlopen(self.ipCatalog+ ':' +  self.portCatalog + '/getStatusFile')
        dataHome = reqHome.read().decode('utf-8')
        filename_ = json.loads(dataHome)
        data = json.load(open(filename_["filename"]))

        for e in data['devicesList']:
            powerList.append({e['deviceName']: e['power']})
        return powerList

        
    exposed = True
    def GET(self, *uri, **params):
        
        #Soglie di temperatura
        reqHome = request.urlopen(self.ipCatalog+ ':' +  self.portCatalog + '/getThreshold')
        dataHome = reqHome.read().decode('utf-8')
        lista_threshold = json.loads(dataHome)

        #informazioni su ON/OFF
        powerList = self.power_OnOff()
        # powerJson = json.dumps(powerList)

        if len(params)!=0 and len(uri)!=0:
            chiave = list(params.keys())[0]
            if uri[0] == 'getHealth' and chiave == 'chatid':
                rooms = self.call_thinkspeak(params['chatid']) 
                for i, room in enumerate(rooms): #cicla sulle room di teamspeak filtrate dall' id della chat
                    for j, rth in enumerate(lista_threshold):  #cicla sulle schedule 
                        if room["deviceName"] == rth["deviceName"]:
                            for e in powerList:
                                powerJson = json.dumps(e)
                                if rth["deviceName"] in powerJson and 'on' in powerJson: 
                                    if 'on' in powerJson:
                                        if int(room["meanTemperature"]) < int(rth["th_sup"]):
                                            room["status"]= "Check the system" 
                                        else:
                                            room["status"]= "Ok" 
                                    else:
                                        rooms = self.call_thinkspeak() 
                                        for i, room in enumerate(rooms):
                                            room["status"]= "off" 
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