import urllib
from urllib import request
import json
import cherrypy


class Environmental():
    def __init__(self) :
        self.threshold = 20
        conf = json.load(open("conf.json"))

        self.ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
        self.portCatalog = conf.get("rest")["HomeCatalog"]["port"]

    #classe per richiamare thinkspeak     
    def call_thinkspeak(self, chatid, room):
        params = {
            'chatid' : chatid}

        query_string = urllib.parse.urlencode( params ) 
        url = self.ipCatalog+ ':' +  self.portCatalog + '/getDevicesList'
        url = url + "?" + query_string 
        reqHome = request.urlopen(url)
        dataHome = reqHome.read().decode('utf-8')
        data = json.loads(dataHome)

        for dev in data:
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
            chiave = list(params.keys())
            if "chatid" in chiave:
                if uri[0] == 'getComfort':
                    
                    feeds = self.call_thinkspeak(params["chatid"], params["room"]) 
                    temp =  float(feeds[-1]['field1']) if feeds[-1]['field1'] != None else float(0)
                    hum =  float(feeds[-1]['field2']) if feeds[-1]['field2'] != None else float(0)
                    co =  float(feeds[-1]['field3']) if feeds[-1]['field3'] != None else float(0)

                    risposta = ""
                    if temp > self.threshold and temp < 23:
                        if hum < 60 and hum > 20: 
                            risposta = "Temperature:"+ str(temp) + '\nHumidity:'+ str(hum) + '\nOptimal comfort'
                        else:
                            risposta = "Temperature:"+ str(temp) + '\nHumidity:'+ str(hum) + '\nHumidity level too high'

                    elif temp < self.threshold and temp > 18:
                        if hum > 60 : 
                            risposta = "Temperature:"+ str(temp) + '\n"Humidity:'+ str(hum) + '\nOptimal comfort'
                        else:
                            risposta =  "Temperature:"+ str(temp) + '\n"Humidity:'+ str(hum) + '\nHumidity level too low'
                
                    elif temp > 23: 
                        risposta = "Too hot"
                    
                    elif temp < 18: 
                        risposta = "Too cold"

                    if co > 1000:
                        risposta += "\nCo level:"+ str(co) + ' ppm' + "\nDangerous quantity, OPEN THE WINDOWS!"  
                    
                    return risposta
            
                elif uri[0] == 'getCOstatus':
                    params = {
                        'chatid' : params["chatid"]}

                    query_string = urllib.parse.urlencode( params ) 
                    url = self.ipCatalog+ ':' +  self.portCatalog + '/getStatusList'
                    url = url + "?" + query_string 
                    reqHome = request.urlopen(url)
                    dataHome = reqHome.read().decode('utf-8')
                    data = json.loads(dataHome)

                    #check status CO
                    for dev in data:
                        statusCO = dev["statusCO"]
                        if statusCO == 'fail':
                            return 'CO level out of range in ' + dev['deviceName']

                    return 'False'


if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    
    cherrypy.config.update({'server.socket_port':8070})
    cherrypy.quickstart(Environmental(), '/', conf)