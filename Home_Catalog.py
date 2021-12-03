import cherrypy

class Calcoliamo(object):

    exposed = True
    def GET(self, *uri, **params):
        if params!={} and len(uri)!=0:  
            keyList = list(params.keys())
            Valuelist = [params[key] for key in params.keys()]

            return Valuelist

    
if __name__=="__main__":
    conf={
        '/':{
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on' : True
        }
    }
    cherrypy.quickstart(Calcoliamo(), '/', conf)
    
    #ciao mi chiamo martina