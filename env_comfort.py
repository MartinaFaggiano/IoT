from email import feedparser
from fileinput import filename
import urllib
from urllib import request
import json
from urllib.parse import urljoin
import cherrypy




# immagazzina in una variabile la risposta dal GET response
class environmental():
    #classe per richiamare thinkspeak
    
    def __init__(self) :
          self.threshold = str(20) 

    def call_thinkspeak(self, room):

        reqHome = request.urlopen('http://127.0.0.1:8080/getDevicesFile')
        dataHome = reqHome.read().decode('utf-8')
        filename_ = json.loads(dataHome)
        data = json.load(open(filename_["filename"]))

        for dev in data["devicesList"]:
            if dev["deviceName"] == room:
                urlJson = dev["channel"]

        response = request.urlopen(urlJson)

        # preleva i dati json dalla richiesta
        data = response.read().decode('utf-8')

        # convertiamo la stringa in dizionario
        data_dict = json.loads(data)

        #separiamo i valori che ci interessano
        feeds = data_dict['feeds']
        
        return feeds

    # def POST(self, *uri, **params):
    
    #     data = cherrypy.request.body.read()
    #     data = json.loads(data)

    #     if len(params)!=0 and len(uri)!=0:
    #         if uri[0] == 'postSchedule':
    #             data = data["schedules"][0]
    #             json_file = json.load(open("schedule.json"))
    #             for schedule in json_file["schedules"]:
    #                 if schedule["deviceName"] == params["room"]:
    #                     schedule["startHour"] = data["startHour"]
    #                     schedule["endHour"] = data["endHour"]
    #             with open("schedule.json", "w") as file:
    #                 json.dump(json_file, file)
    
    exposed = True
    def GET(self, *uri, **params):

        reqHome = request.urlopen('http://127.0.0.1:8080/getThreshold')
        dataHome = reqHome.read().decode('utf-8')
        lista_threshold = json.loads(dataHome)
        
        if len(params)!=0 and len(uri)!=0:
            chiave = list(params.keys())[0]
            if chiave == "room":
                if uri[0] == 'getComfort':
                    
                    feeds = self.call_thinkspeak(params["room"]) 
                    temp =  float(feeds[1]['field1'])
                    # hum =  float(feeds[1]['field2'])
                    # co =  float(feeds[1]['field3'])

                    if temp > 20:
                        return "VALORE OTTIMALE"

                    # if temp > self.threshold and temp < 23: #TODO 
                    #     if hum < 60 and hum > 20: 
                    #         return "Temperature:"+ temp + '\n"Humidity:'+ hum + '\nOttimal comfort'
                    #     else:
                    #         return "Temperature:"+ temp + '\n"Humidity:'+ hum + '\nHumidity level too high'

                    # elif temp < self.threshold and temp > 18:
                    #     if hum > 60 : 
                    #         return "Temperature:"+ temp + '\n"Humidity:'+ hum + '\nOttimal comfort'
                    #     else:
                    #         return "Temperature:"+ temp + '\n"Humidity:'+ hum + '\nHumidity level too low'
                    
                    # if co > 33:
                    #     return "Co level:"+ temp + "\nLevel is too hight, OPEN THE WINDOWS!"  
        
  
if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    
    cherrypy.config.update({'server.socket_port':8070})
    cherrypy.quickstart(environmental(), '/', conf)
