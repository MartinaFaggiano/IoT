import sched
import cherrypy
import json


class HomeCatalog(object):

    def __init__(self) -> None:
          pass

    exposed = True
    def GET(self, *uri, **params):
        

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
    
            elif uri[0]=="getTopicsList":
                data = json.load(open("MQTT-topics.json"))
                self.topics = []
                for topic in data["Topics"]:
                     self.topics.append(topic)

                return json.dumps(self.topics)

            elif uri[0] == "getSchedules":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                for schedule in data["schedules"]:
                    self.schedules.append(schedule)
   
                return json.dumps(self.schedules)
            

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

        if params=={} and len(uri)!=0:  

            if uri[0]=="postTopicsList":
                self.topics.append(data)
                json_file = json.load(open("MQTT-topics.json"))
                json_file["topicsList"] = self.topics
                print(json_file)
                with open("topics.json", "w") as file:
                    json.dump(json_file, file)

            elif uri[0] == "postAddDevice": 
                nDev = len(data)

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
                    "sensorName": "CO2",
                    "measureType": "level",
                    "deviceID": str(nDev),
                    "unit": "%"
                }]
                json_file = json.load(open("devices.json"))
                json_file["devicesList"] = data
                print(json_file)
                with open("devices.json", "w") as file:
                    json.dump(json_file, file)

        

            elif uri[0] == "postSchedule": 
                # self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["schedules"] = data["schedules"]
                
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)       
                    
    


        # data = cherrypy.request.body.read()
        # data = json.loads(data)
        # self.devices.append(data)
        # print(self.devices)

        # json_file = json.load(open("devices.json"))
        # json_file["devicesList"] = self.devices
        # print(json_file)
        # with open("devices.json", "w") as pippo:
        #     json.dump(json_file, pippo)

    
if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    cherrypy.quickstart(HomeCatalog(), '/', conf)
