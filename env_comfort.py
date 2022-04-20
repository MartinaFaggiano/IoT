from email import feedparser
import urllib
from urllib import request
import json
import cherrypy




# immagazzina in una variabile la risposta dal GET response
class environmental():
    #classe per richiamare thinkspeak
    
    def __init__(self) :
          self.threshold = str(23.5)

    def call_thinkspeak(self):
        response = request.urlopen('https://api.thingspeak.com/channels/1669938/feeds.json?api_key=4D9OPXEJK7T63SVN&results=2')

        # preleva i dati json dalla richiesta

        data = response.read().decode('utf-8')

        # convertiamo la stringa in dizionario

        data_dict = json.loads(data)

        #separiamo i valori che ci interessano

        feeds = data_dict['feeds']
        
        return feeds

        #facciamo reagire alla pressione del pulsante
        

        # if(query_data == 'temp'):
        #     self.bot.sendMessage(from_id, text='La Temperatura è di: ' + feeds[1]['field1'] + '°C')
            
        # elif(query_data == 'umid'):
        #     self.bot.sendMessage(from_id, text="L'Umidità è il: " + feeds[1]['field2'] + '%')
            
        # elif(query_data == 'co'):
        #     self.bot.sendMessage(from_id, text='La Pressione è di: ' + feeds[1]['field3'] + ' mbar')
            
        #print(feeds) #printa le ultime due temperature misurate
        
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
        
        if len(params)==0 and len(uri)!=0:
            
            if uri[0] == 'getComfort':
                
                feeds = self.call_thinkspeak() 

            
                if feeds[1]['field1'] == self.threshold:
                
                    return 'Temperatura ottimale'
                if feeds[1]['field1'] <  self.threshold:
                    
                    return 'La temperatura è di '+ feeds[1]['field1'] + '\n si consiglia di accendere il riscaldamento'
                
                if feeds[1]['field1'] > self.threshold:
                    
                    return "La temperatura è di "+ feeds[1]['field1'] + '\n si consiglia di spegnere il riscaldamento'
                
            


        
  
if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    
    cherrypy.config.update({'server.socket_port':8070})
    cherrypy.quickstart(environmental(), '/', conf)
