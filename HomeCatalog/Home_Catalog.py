import cherrypy
import json


class HomeCatalog(object):

    def __init__(self) -> None:
        json_file = json.load(open("devices.json"))
        self.nDev = json_file["devicesList"][-1]["deviceID"]

    exposed = True
    def GET(self, *uri, **params):
        
        if len(uri)!=0:  
            if uri[0] == "getnDev": 
                return str(self.nDev)

            elif uri[0] == "postDELDevice":  #Delete the specified devices
                chiave = list(params.keys())[0]
                if chiave == 'room':
                    chatid = params['chatid']
                    nDev = params['room']
                    json_file = json.load(open("devices.json"))
                    data = []
                    for e in json_file['devicesList']: 
                        if nDev not in e['deviceName']:
                            data.append(e)
                        else: 
                            channels = json.load(open("channels.json"))
                            num =  nDev.split('_')[1]
                            for channel in channels["channelList"]: 
                                if e["channel"] in channel["code"]: 
                                    channel["status"] = "idle"
                            devID = e['deviceID']

                            with open("channels.json", "w") as file:
                                json.dump(channels, file)  

                    for el in json_file['usersList']: 
                        for house in el['houses']: 
                            if house['chatID'] == chatid: 
                                houseid = house['houseID']

                    for house in json_file['housesList']: 
                        if houseid == house['houseID']:
                            devList = list(house['devicesListID'])
                            devList.pop(devList.index(devID)) 
                            house['devicesListID'] = devList
                    
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
                            elif params['sensor'] == 'hum':
                                topic = dev["topic"]['humidity']
                            elif params['sensor'] == 'co':
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
                
                elif uri[0] == 'getPower':
                    json_file = json.load(open("status.json"))
                    for dev in json_file['devicesList']:
                        if dev["deviceName"] == params["room"]:
                            dev['power'] = params['status']
                    with open("status.json", "w") as file:
                        json.dump(json_file, file)

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


            elif chiave == "mod":
                if uri[0] == 'getSchedules':
                    data = json.load(open("schedule.json"))
                    self.schedules = []
                    self.schedules.append(data["modify_schedules"][0][params["mod"]])
                    return json.dumps(self.schedules)

            elif chiave == 'chatid' and uri[0] == "getDevicesList":  
                data = json.load(open("devices.json"))

                houseID = 0
                for user in data['usersList']:
                    for house in user['houses']: 
                        if house['chatID'] == params["chatid"]: 
                            houseID = house['houseID']

                for house in data['housesList']:
                    if house['houseID'] == houseID: 
                        devList = list(house['devicesListID'])

                devices = []
                for device in data["devicesList"]:
                    if device['deviceID'] in devList: 
                        devices.append(device) 
                return json.dumps(devices)


            elif chiave == 'chatid' and uri[0] == "getStatusList":  
                data = json.load(open("devices.json"))

                houseID = 0
                for user in data['usersList']:
                    for house in user['houses']: 
                        if house['chatID'] == params["chatid"]: 
                            houseID = house['houseID']

                for house in data['housesList']:
                    if house['houseID'] == houseID: 
                        devList = list(house['devicesListID'])

                statusList = json.load(open("status.json"))

                statusDev = []
                for device in statusList["devicesList"]:
                    if device['deviceID'] in devList: 
                        statusDev.append(device)

                return json.dumps(statusDev)
            

                
        
        if params=={} and len(uri)!=0:  

            if uri[0] == "getSchedules":    
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

            elif uri[0] == "getChannels":  
                data = json.load(open("channels.json"))
                self.channels = []
                for ch in data["channelList"]:
                    self.channels.append(ch) 
                return json.dumps(self.channels)
            

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

            #crea nuovo dispositivo e aggiunge schedule di default
            if uri[0] == "postAddDevice": 
                chiave = list(params.keys())[0]
                if chiave == "chatid":
                    chatid = params['chatid']

                    data[-1]["device"] = [{
                        "sensorName": "Temp",
                        "measureType": "temp",
                        "unit": "C"
                    },
                    {
                        "sensorName": "Humidity",
                        "measureType": "hum",
                        "unit": "%"
                    },
                    {
                        "sensorName": "CO",
                        "measureType": "level",
                        "unit": "%",
                        "alarm" : "off"
                    }]
                    #aggiunta canale
                    channels = json.load(open("channels.json"))
                    for chan in channels["channelList"]: 
                        if chan["id"] == data[-1]["deviceName"].split('_')[1]:
                            data[-1]["channel"] = chan["code"]
                            chan["status"] = "busy"
                    with open("channels.json", "w") as file:
                        json.dump(channels, file)   

                    #aggiunta topic
                    topic = {
                        "heating" : "iot/heating_system/"+ data[-1]["deviceName"],
                        "co" : "iot/co_control/"+ data[-1]["deviceName"],
                        "humidity" : "iot/humidity_control/"+ data[-1]["deviceName"]}
                    data[-1]["topic"] = topic

                    json_file = json.load(open("devices.json"))
                    json_file["devicesList"].append(data[-1])

                    houseID = 0
                    for user in json_file['usersList']:
                        for house in user['houses']: 
                            if house['chatID'] == chatid: 
                                houseID = house['houseID']

                    for house in json_file['housesList']:
                        if house['houseID'] == houseID: 
                            devList = list(house['devicesListID'])
                            devList.append(int(data[-1]["deviceID"]))
                            house['devicesListID'] = devList

                    with open("devices.json", "w") as file:
                        json.dump(json_file, file)

                    #ggiunta schedule di default per nuovo dispositivo
                    sched = {"deviceName": data[-1]["deviceName"],
                    "startHour":"08:00:00",
                    "endHour":"10:00:00",
                    "th_inf":"18",
                    "th_sup":"21"}
                    json_file = json.load(open("schedule.json"))
                    json_file["schedules"].append(sched)
                    with open("schedule.json", "w") as file:
                        json.dump(json_file, file)                      

                    dataStatus = {
                        "deviceName": data[-1]["deviceName"],
                        "deviceID": int(data[-1]["deviceID"]),
                        "statusCO": "ok",
                        "power": "on"
                    }

                    json_file = json.load(open("status.json"))
                    print(json_file['devicesList'])
                    json_file["devicesList"].append(dataStatus)
                    with open("status.json", "w") as file:
                        json.dump(json_file, file)

                    self.nDev += 1
                    return "successfully added"

        elif uri[0] == 'postStatus':
                room = data["room"]
                statusCO = data["status"]

                json_file = json.load(open("status.json"))
                for dev in json_file["devicesList"]:
                    if dev["deviceName"] == room:
                        dev["statusCO"] = statusCO
                with open("status.json", "w") as file:
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

            if uri[0] == "postSchedule": 
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