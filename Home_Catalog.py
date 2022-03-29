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
        if params=={} and len(uri)!=0:  
            if uri[0] == "getSensorsList":  
                data = json.load(open("devices.json"))
                self.sensors = []
                for device in data["devicesList"]:
                    self.devices.append(device) 
                     
                return json.dumps(self.sensors)
    
            elif uri[0]=="getTopicsList":
                data = json.load(open("MQTT-topics.json"))
                self.topics = []
                for topic in data["Topics"]:
                     self.topics.append(topic)

                return json.dumps(self.topics)

            elif uri[0] == "getDevicesList":   
                data = json.load(open("sensors.json"))
                self.devices = []
                for sensor in data["sensorsList"]:
                    self.sensors.append(sensor)    
                return json.dumps(self.devices)

            elif uri[0] == "getSchedules":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                for schedule in data["schedules"]:
                    self.schedules.append(schedule)
   
                return json.dumps(self.schedules)

            elif uri[0] == "getModifyMorning":    
                data = json.load(open("schedule.json"))
                self.schedules = []
                for schedule in data["schedules"]:
                    self.schedules.append(schedule)
   
                return json.dumps(self.schedules)
    

    def POST(self, *uri, **params):

        data = cherrypy.request.body.read()
        data = json.loads(data)

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
                    
            elif uri[0] == "postModify_schedule_morning": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["morning"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)  
                
            elif uri[0] == "postModify_schedule_afternoon": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["afternoon"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)  
                    
            elif uri[0] == "postModify_schedule_evening": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["evening"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)  
                    
            elif uri[0] == "postModify_schedule_night": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["night"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)     
                    
            elif uri[0] == "postModify_schedule_allday": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["allday"] = self.schedules
                print(json_file)
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
