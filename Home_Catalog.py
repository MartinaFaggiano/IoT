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
        data = json.load(open("devices.json"))
        self.devices = []
        for device in data["devicesList"]:
            self.devices.append(device)  
        
        data = json.load(open("MQTT-topics.json"))
        self.topics = []
        for topic in data["Topics"]:
            self.topics.append(topic)

        data = json.load(open("sensors.json"))
        self.sensors = []
        for sensor in data["sensorsList"]:
            self.sensors.append(sensor)

        data = json.load(open("schedule.json"))
        self.schedules = []
        for schedule in data["schedules"]:
            self.schedules.append(schedule)

    exposed = True
    def GET(self, *uri, **params):
        if params=={} and len(uri)!=0:  
            if uri[0] == "get/sensorsList":        
                return json.dumps(self.sensors)
    
            elif uri[0]=="get/topicsList":
                return json.dumps(self.topics)

            elif uri[0] == "get/devicesList":       
                return json.dumps(self.devices)

            elif uri[0] == "get/schedules":       
                return json.dumps(self.schedules)
    

    def POST(self, *uri, **params):

        data = cherrypy.request.body.read()
        data = json.loads(data)

        if params=={} and len(uri)!=0:  
            if uri[0] == "post/sensorsList":
                self.sensors.append(data)
                json_file = json.load(open("sensors.json"))
                json_file["sensorsList"] = self.sensors
                print(json_file)
                with open("sensors.json", "w") as file:
                    json.dump(json_file, file)
    
            elif uri[0]=="post/topicsList":
                self.topics.append(data)
                json_file = json.load(open("MQTT-topics.json"))
                json_file["topicsList"] = self.topics
                print(json_file)
                with open("topics.json", "w") as file:
                    json.dump(json_file, file)

            elif uri[0] == "post/devicesList": 
                self.devices.append(data)
                json_file = json.load(open("devices.json"))
                json_file["devicesList"] = self.devices
                print(json_file)
                with open("devices.json", "w") as file:
                    json.dump(json_file, file)

            elif uri[0] == "post/schedule": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["schedules"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)       
                    
            elif uri[0] == "post/modify_schedule_morning": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["morning"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)  
                
            elif uri[0] == "post/modify_schedule_afternoon": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["afternoon"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)  
                    
            elif uri[0] == "post/modify_schedule_evening": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["evening"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)  
                    
            elif uri[0] == "post/modify_schedule_night": 
                self.schedules.append(data)
                json_file = json.load(open("schedule.json"))
                json_file["modify_schedules"]["night"] = self.schedules
                print(json_file)
                with open("schedule.json", "w") as file:
                    json.dump(json_file, file)     
                    
            elif uri[0] == "post/modify_schedule_allday": 
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
