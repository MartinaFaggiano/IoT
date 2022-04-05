import sched
import cherrypy
import json


# class Device():
#     def __init__(self, id, name, measure, unit):
#         self.id = id
#         self.name = name
#         self.measure = measure
#         self.unit = unit

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

            elif uri[0] == "getSensorsList":   
                data = json.load(open("sensors.json"))
                self.sensors = []
                for sensor in data["sensorsList"]:
                    self.sensors.append(sensor)    
                return json.dumps(self.sensors)

            elif uri[0] == "getSchedules":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                for schedule in data["schedules"]:
                    self.schedules.append(schedule)
   
                return json.dumps(self.schedules)

            elif uri[0] == "getModifyMorning":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                modify_morning = data["modify_schedules"]['morning']
                self.schedules.append(modify_morning)
   
                return json.dumps(self.schedules)
            
            elif uri[0] == "getModifyAfternoon":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                modify_afternoon = data["modify_schedules"]['afternoon']
                self.schedules.append(modify_afternoon)
   
                return json.dumps(self.schedules)
            
            elif uri[0] == "getModifyEvening":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                modify_evening = data["modify_schedules"]['evening']
                self.schedules.append(modify_evening)
   
                return json.dumps(self.schedules)
             
            elif uri[0] == "getModifyNight":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                modify_night = data["modify_schedules"]['night']
                self.schedules.append(modify_night)
   
                return json.dumps(self.schedules)
            
            
            elif uri[0] == "getModifyAllday":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                modify_allday = data["modify_schedules"]['allday']
                self.schedules.append(modify_allday)
   
                return json.dumps(self.schedules)
            
    

    def POST(self, *uri, **params):

        data = cherrypy.request.body.read()
        data = json.loads(data)

        if len(params)!=0 and len(uri)!=0:
            if uri[0] == 'postSchedule':
                data = data["schedules"][0]
                print("aaaaaa", data)
                json_file = json.load(open("schedule.json"))
                for schedule in json_file["schedules"]:
                    if schedule["deviceName"] == params["room"]:
                        schedule["startHour"] = data["startHour"]
                        schedule["endHour"] = data["endHour"]
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)

        if params=={} and len(uri)!=0:  
            if uri[0] == "postSensorsList":
                self.sensors.append(data)
                json_file = json.load(open("sensors.json"))
                json_file["sensorsList"] = self.sensors
                print(json_file)
                with open("sensors.json", "w") as file:
                    json.dump(json_file, file)
    
            elif uri[0]=="postTopicsList":
                self.topics.append(data)
                json_file = json.load(open("MQTT-topics.json"))
                json_file["topicsList"] = self.topics
                print(json_file)
                with open("topics.json", "w") as file:
                    json.dump(json_file, file)

            elif uri[0] == "postDevicesList": 
                self.devices.append(data)
                json_file = json.load(open("devices.json"))
                json_file["devicesList"] = self.devices
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
