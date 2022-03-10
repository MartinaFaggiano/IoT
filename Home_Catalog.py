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


    exposed = True
    def GET(self, *uri, **params):
        if params=={} and len(uri)!=0:  
            if uri[0] == "sensorsList":        
                return json.dumps(self.sensors)
    
            elif uri[0]=="topicsList":
                return json.dumps(self.topics)


            elif uri[0] == "devicesList":       
                return json.dumps(self.devices)
    

    def POST(self, *uri, **params):

        data = cherrypy.request.body.read()
        data = json.loads(data)

        if params=={} and len(uri)!=0:  
            if uri[0] == "sensorsList":
                self.sensors.append(data)
                json_file = json.load(open("sensors.json"))
                json_file["sensorsList"] = self.sensors
                print(json_file)
                with open("sensors.json", "w") as file:
                    json.dump(json_file, file)
    
            elif uri[0]=="topicsList":
                self.topics.append(data)
                json_file = json.load(open("MQTT-topics.json"))
                json_file["topicsList"] = self.topics
                print(json_file)
                with open("topics.json", "w") as file:
                    json.dump(json_file, file)

            elif uri[0] == "devicesList": 
                self.devices.append(data)
                json_file = json.load(open("devices.json"))
                json_file["devicesList"] = self.devices
                print(json_file)
                with open("devices.json", "w") as pippo:
                    json.dump(json_file, pippo)


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
