import cherrypy
import json


class HomeCatalog(object):

    def __init__(self) -> None:
          pass

    exposed = True
    def GET(self, *uri, **params):
        
        if len(uri)!=0:  

            if uri[0] == "postDELDevice":  #Delete the specified devices
                chiave = list(params.keys())[0]
                if chiave == 'room':

                    nDev = params['room']
                    json_file = json.load(open("devices.json"))
                    data = []
                    for e in json_file['devicesList']: 

                        if nDev not in e['deviceName']:
                            data.append(e)
                        else: 
                            ch = e['channel']
                            channels = json.load(open("channels.json"))
                            num =  nDev.split('_')[1]
                            channels["channel"][0][str(num)] = ch

                            with open("channels.json", "w") as file:
                                json.dump(channels, file)                   
            

                    json_file = json.load(open("devices.json"))
                    json_file["devicesList"] = data
                    with open("devices.json", "w") as file:
                        json.dump(json_file, file)

                    json_file = json.load(open("schedule.json"))
                    data = []
                    for e in json_file['schedules']: 

                        if nDev not in e['deviceName']:
                            data.append(e)

                    json_file["schedules"] = data
                    with open("schedule.json", "w") as file:
                        json.dump(json_file, file)                    
    

                    json_file = json.load(open("status.json"))
                    data = []
                    for e in json_file['devicesList']:
                        if nDev not in e['deviceName']:
                            data.append(e)

                    json_file["devicesList"] = data
                    with open("status.json", "w") as file:
                        json.dump(json_file, file)

                    return "successfully deleted"

        if len(params)!=0 and len(uri)!=0:
            chiave = list(params.keys())[0]
            if chiave == "room":
                if uri[0] == 'getSchedules':
                    data = json.load(open("schedule.json"))
                    self.schedules = []
                    for schedule in data["schedules"]:
                        if schedule["deviceName"] == params["room"]:
                            self.schedules.append(schedule)
                    print(self.schedules)
                    return json.dumps(self.schedules)

                #get per ottenere topic di una specifica stanza
                elif uri[0] == 'getDevices':
                    data = json.load(open("devices.json"))
                    for dev in data["devicesList"]:
                        if dev["deviceName"] == params["room"]:
                            if params['sensor'] == 'temp':
                                topic = dev["topic"]['heating']
                            elif params['sensor'] == 'humidity':
                                topic = dev["topic"]['humidity']
                            else :
                                topic = dev["topic"]['co']
                    return json.dumps(topic)

                elif uri[0] == 'getThreshold':
                    data = json.load(open("schedule.json"))
                    self.schedules = []
                    for schedule in data["schedules"]:
                        if schedule["deviceName"] == params["room"]:
                            th = {
                                "th_inf" : schedule["th_inf"],
                                "th_sup" : schedule["th_sup"]
                            }

                    return json.dumps(th)

            elif chiave == "rooms":
                if uri[0] == 'getDevices':
                    data = json.load(open("devices.json"))
                    if 'all' == params["rooms"]:
                        topics = []
                        for dev in data["devicesList"]:
                                if params['sensor'] == 'temp':
                                    topics.append(dev["topic"]['heating'])
                                elif params['sensor'] == 'humidity':
                                    topics.append(dev["topic"]['humidity'])
                                else :
                                    topics.append(dev["topic"]['co'])
                    return json.dumps(topics)





            if chiave == "mod":
                if uri[0] == 'getSchedules':
                    data = json.load(open("schedule.json"))
                    self.schedules = []
                    self.schedules.append(data["modify_schedules"][0][params["mod"]])
                    return json.dumps(self.schedules)


                
        
        if params=={} and len(uri)!=0:  
            if uri[0] == "getDevicesList":  
                data = json.load(open("devices.json"))
                self.devices = []
                for device in data["devicesList"]:
                    self.devices.append(device) 
                return json.dumps(self.devices)

            if uri[0] == "getDevicesFile":  
                filename = {
                    "filename": "devices.json"
                    }
                return json.dumps(filename)
            elif uri[0] == "getStatusFile":  
                filename = {
                    "filename": "status.json"
                    }
                return json.dumps(filename)


            elif uri[0] == "getSchedules":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                for schedule in data["schedules"]:
                    self.schedules.append(schedule)
   
                return json.dumps(self.schedules)
            
            elif uri[0] == 'getThreshold':
                data = json.load(open("schedule.json"))
                self.ths = []
                for schedule in data["schedules"]:
                        th = {
                            "deviceName": schedule["deviceName"],
                            "th_inf" : schedule["th_inf"],
                            "th_sup" : schedule["th_sup"]
                        }
                        self.ths.append(th)

                return json.dumps(self.ths)
            

    def POST(self, *uri, **params):

        data = cherrypy.request.body.read()
        data = json.loads(data)

        if len(params)!=0 and len(uri)!=0:
            if uri[0] == 'postSchedule':
                data = data["schedules"][0]
                json_file = json.load(open("schedule.json"))
                for schedule in json_file["schedules"]:
                    if schedule["deviceName"] == params["room"]:
                        schedule["startHour"] = data["startHour"]
                        schedule["endHour"] = data["endHour"]
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)

        if uri[0] == 'postThreshold':
                data = data["schedules"][0]
                json_file = json.load(open("schedule.json"))
                for schedule in json_file["schedules"]:
                    if schedule["deviceName"] == params["room"]:
                        schedule["th_inf"] = data["th_inf"]
                        schedule["th_sup"] = data["th_sup"]
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)


        if params=={} and len(uri)!=0:  

            if uri[0] == "postAddDevice":  #crea nuovo dispositivo, e aggiunge schedule di default
                nDev = len(data)

                if nDev > 3:
                    return "unsuccessfully added"
                else:
                    data[nDev-1]["device"] = [{
                        "sensorName": "Temp",
                        "measureType": "temp",
                        "deviceID": str(nDev),
                        "unit": "C"
                    },
                    {
                        "sensorName": "Humidity",
                        "measureType": "hum",
                        "deviceID": str(nDev),
                        "unit": "%"
                    },
                    {
                        "sensorName": "CO",
                        "measureType": "level",
                        "deviceID": str(nDev),
                        "unit": "%",
                        "alarm" : "off"
                    }]
                    #aggiunta canale
                    channels = json.load(open("channels.json"))
                    ch = channels["channel"][0][str(nDev)]
                    data[nDev-1]["channel"] = ch
                    
                    channels["channel"][0][str(nDev)] = ''
                    with open("channels.json", "w") as file:
                        json.dump(channels, file)   

                    #aggiunta topic
                    topic = {
                        "heating" : "iot/heating_sistem/"+ data[nDev-1]["deviceName"],
                        "co" : "iot/co_control/"+ data[nDev-1]["deviceName"],
                        "humidity" : "iot/humidity_control/"+ data[nDev-1]["deviceName"]}
                    data[nDev-1]["topic"] = topic

                    json_file = json.load(open("devices.json"))
                    json_file["devicesList"] = data
                    with open("devices.json", "w") as file:
                        json.dump(json_file, file)

                    #ggiunta schedule di default per nuovo dispositivo
                    sched = {"deviceName": data[nDev-1]["deviceName"],
                    "startHour":"08:00:00",
                    "endHour":"10:00:00",
                    "th_inf":"18",
                    "th_sup":"21"}
                    json_file = json.load(open("schedule.json"))
                    json_file["schedules"].append(sched)
                    with open("schedule.json", "w") as file:
                        json.dump(json_file, file) #carica il file, aggiornando solo la lista schedules                        
    
                    dataStatus = {
                        "deviceName": data[nDev-1]["deviceName"],
                        "statusCO": "ok",
                        "power": "on"
                    }

                    json_file = json.load(open("status.json"))
                    print(json_file['devicesList'])
                    json_file["devicesList"].append(dataStatus)
                    with open("status.json", "w") as file:
                        json.dump(json_file, file)

                    return "successfully added"
       

            elif uri[0] == "postSchedule": 
                json_file = json.load(open("schedule.json"))
                json_file["schedules"] = data["schedules"]
                
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)       
                    
if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    cherrypy.config.update({'server.socket_host': '192.168.43.77'})
    cherrypy.config.update({'server.socket_port':8080})
    cherrypy.tree.mount(HomeCatalog(), '/', conf)
    cherrypy.engine.start()