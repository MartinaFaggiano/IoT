import cherrypy
import json


class Device():
    def __init__(self, id, name, measure, unit):
        self.id = id
        self.name = name
        self.measure = measure
        self.unit = unit

class HomeCatalog(object):

    exposed = True
    def GET(self, *uri):
        if uri[0]=="devicesList":
            data = json.load(open("devices.json"))
            self.devices = []
            for device in data["devicesList"]:
                # Device(device["deviceID"], device["deviceName"], device["measureType"], device["unit"])
                self.devices.append(device)
            return self.devices


    # def GET(self, *uri):
    #     if uri[0]=="topicsList":
    #         data = json.load(open("MQTT-topics.json"))
    #         self.topics = []
    #         for topic in data["Topics"]:
    #             self.topics.append(topic)
    #         return self.topics

    def POST(self, id, name, type, unit):
        print(id, name, type, unit)

        data = cherrypy.request.body.read()
        data = json.loads(data)
        self.devices.append(data)
        print(self.devices)

        json_file = json.load(open("devices.json"))
        json_file["devicesList"] = self.devices
        print(json_file)
        with open("devices.json", "w") as pippo:
            json.dump(json_file, pippo)

    
if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    cherrypy.quickstart(HomeCatalog(), '/', conf)
