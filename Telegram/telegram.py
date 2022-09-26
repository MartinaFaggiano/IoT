import json
import time
import threading
import telepot
from urllib import request, parse
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from dateutil import parser

class TelegramClass(threading.Thread):
    class Co_control(threading.Thread):
        def __init__(self, fromID, bot):
            threading.Thread.__init__(self)
            self.from_id = fromID
            self.bot = bot
            conf = json.load(open("conf.json"))

            self.ipEnv = conf.get("rest")["Env"]["ip"]
            self.portEnv = conf.get("rest")["Env"]["port"]

        def run(self):
            while(1):
                params = {
                    'chatid' : self.from_id}
                query_string = parse.urlencode( params ) 
                url = self.ipEnv+ ':' +  self.portEnv + '/getCOstatus'
                url = url + "?" + query_string 

                reqHome = request.urlopen(url)
                dataHome = reqHome.read().decode('utf-8')
                if dataHome != 'False':
                    self.bot.sendMessage(self.from_id, text=dataHome)
                    
                time.sleep(180)

    def __init__(self):
        self.deviceName = ""
        self.chatIDs = []
        self.th_inf = "m"
        self.th_sup = "n"
        self.next = ""
        self.from_id = ""
        
        conf = json.load(open("conf.json"))   
        self.tokenBot = conf.get("telegram")["token"]     
        self.ipCatalog = conf.get("rest")["HomeCatalog"]["ip"]
        self.portCatalog = conf.get("rest")["HomeCatalog"]["port"]

        self.ipHealth = conf.get("rest")["Health"]["ip"]
        self.portHealth = conf.get("rest")["Health"]["port"]

        self.ipEnv = conf.get("rest")["Env"]["ip"]
        self.portEnv = conf.get("rest")["Env"]["port"]

        self.bot = telepot.Bot(self.tokenBot)

        MessageLoop(self.bot, {'chat': self.on_chat_message,
                'callback_query': self.on_callback_query}).run_as_thread()
   

    #la funzione on_chat_message crea una inline keyboard
    def on_chat_message(self, msg):

        content_type, chat_type, chat_id = telepot.glance(msg)
        self.from_id = chat_id

        self.Threads = self.Co_control(self.from_id,self.bot)
        self.Threads.start()
        if chat_id not in self.chatIDs:
            self.chatIDs.append(chat_id)
        message = msg['text']
        if message == "Menu":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Temperature', callback_data='temp')],
                [InlineKeyboardButton(text='Umidity', callback_data='umid')],
                [InlineKeyboardButton(text='CO level', callback_data='co')],
                [InlineKeyboardButton(text='Threshold', callback_data='threshold')],
                [InlineKeyboardButton(text='Schedule', callback_data='sched')],
                [InlineKeyboardButton(text='Comfort', callback_data='getComfort')],
                [InlineKeyboardButton(text='Control System Health', callback_data='getHealth')],
                [InlineKeyboardButton(text='Add new device', callback_data='newDevice')],
                [InlineKeyboardButton(text='Delete a device', callback_data='delDev')]

            ])

            self.bot.sendMessage(chat_id, 'Use the menu to manage your Smart Home system', reply_markup=keyboard)

        elif message.split(" ")[0].isnumeric():
            self.th_inf = message.split(" ")[0]
            self.th_sup = message.split(" ")[1]
            if('modThreshold' in self.next):

                json_data = json.dumps( {"schedules": [
                {
                    "deviceName": self.deviceName,
                    "th_inf": self.th_inf,
                    "th_sup": self.th_sup
                }]})  
                params = {
                    'room' : self.deviceName}
                query_string = parse.urlencode( params ) 
                url = self.ipCatalog+ ':' +  self.portCatalog + '/postThreshold'
                url = url + "?" + query_string 

                re = requests.post(url, 
                        data = json_data,
                )

                self.th_inf = "m"
                self.th_sup = "n"

                self.bot.sendMessage(chat_id, text= "Thresholds modified")


    #la funzione on_callback_query processa i dati da Thingspeak e reagisce a seconda del pulsante premuto
        
    def on_callback_query(self, msg):
        #facciamo reagire alla pressione del pulsante
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        self.from_id = from_id
        print('Callback Query:', query_id, from_id, query_data)

        #recupera i dati da thingspeak
        feeds = []
        roomID = []
        if query_data == 'temp' or query_data == 'umid' or query_data == 'co': 

            params = {
                'chatid' : self.from_id}
            query_string = parse.urlencode( params ) 
            url = self.ipCatalog+ ':' +  self.portCatalog + '/getDevicesList' + "?" + query_string
            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            lista_device = json.loads(dataHome)

            for ch in lista_device:
                roomID.append(ch['deviceName'])
                data_dict = json.loads(request.urlopen(ch['channel']).read().decode('utf-8'))
                feeds.append(data_dict['feeds'])

        #BUTTON
        if(query_data == 'temp'):
            cont = 1
            for feed in feeds: 
                if feed:
                    dataOra = str(parser.isoparse(feed[-1]['created_at'])) 
                    self.bot.sendMessage(from_id, text= dataOra.split('+')[0] + ': The temperature in '+ str(roomID[cont-1]) +' is ' + feed[-1]['field1'] + '°C')
                cont += 1

        #BUTTON
        elif(query_data == 'umid'):
            cont = 1
            for feed in feeds: 
                if feed:
                    dataOra = str(parser.isoparse(feed[-1]['created_at'])) 
                    self.bot.sendMessage(from_id, text= dataOra.split('+')[0] + ': The humidity in '+ str(roomID[cont-1]) +' is ' + feed[-1]['field2'] + '%')
                cont += 1
            
        #BUTTON   
        elif(query_data == 'co'):
            cont = 1
            for feed in feeds: 
                if feed:
                    dataOra = str(parser.isoparse(feed[-1]['created_at'])) 
                    self.bot.sendMessage(from_id, text= dataOra.split('+')[0] + ': The CO level in '+ str(roomID[cont-1]) +' is ' + feed[-1]['field3'] + 'ppm')
                cont += 1

            
        if query_data == "sched" or query_data == "getComfort" or query_data == "threshold" or query_data == "delDev":
            self.utility = query_data
            params = {
                'chatid' : self.from_id}
            query_string = parse.urlencode( params ) 
            url = self.ipCatalog+ ':' +  self.portCatalog + '/getDevicesList'
            url = url + "?" + query_string 
            print(url)
            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            lista_device = json.loads(dataHome)
            buttons = [[]]
            for dev in lista_device:
                buttons[0].append(InlineKeyboardButton(text=dev["deviceName"], callback_data=dev["deviceName"])) 

            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(from_id, text='Choose a room', reply_markup=keyboard)
          
        
        if('RoomSystem' in query_data):
            self.deviceName = query_data 
            if self.utility == "sched": 
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Display schedule', callback_data= 'get_schedule_heating')],
                        [InlineKeyboardButton(text='Modify', callback_data='post_schedule_heating')]
                    ])

                x = self.bot.sendMessage(from_id, 'Use the below menu', reply_markup=keyboard)
            elif self.utility == "getComfort":
                params = {
                    'chatid' : self.from_id,
                    'room' : self.deviceName}
                query_string = parse.urlencode( params ) 
                url = self.ipEnv+ ':' +  self.portEnv + '/getComfort'
                url = url + "?" + query_string 
                reqHome = request.urlopen(url)
                dataHome = reqHome.read().decode('utf-8')

                self.bot.sendMessage(from_id, text = dataHome)

            elif self.utility == "threshold":
                params = {
                    'room' : self.deviceName}
                query_string = parse.urlencode( params ) 
                url = self.ipCatalog+ ':' +  self.portCatalog + '/getThreshold'
                url = url + "?" + query_string 

                reqHome = request.urlopen(url)
                dataHome = json.loads(reqHome.read().decode('utf-8'))

                self.bot.sendMessage(from_id, text = "Current operating threshold of the heating system")
                self.bot.sendMessage(from_id, text = dataHome['th_inf'] + ' - ' + dataHome['th_sup'])

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Modify thresholds heating system', callback_data= 'modThresholdMess')]
                    ])
                
                x = self.bot.sendMessage(from_id, 'To modify the settings uses the below button', reply_markup=keyboard)
                
            elif self.utility == "delDev":
                params = {
                    'room' : self.deviceName,
                    'chatid' : from_id}
                query_string = parse.urlencode( params ) 
                url = self.ipCatalog+ ':' +  self.portCatalog + '/postDELDevice'
                url = url + "?" + query_string 

                reqHome = request.urlopen(url)
                dataHome = reqHome.read().decode('utf-8')

                self.bot.sendMessage(from_id, text = "Request processed")

        if('modThresholdMess' in query_data):

            self.bot.sendMessage(from_id, text= "Insert threshold separated by a white space. Like '15 21':")
            self.next = "modThreshold"
                  
              
        if(query_data == 'get_schedule_heating'):
            params = {
                'room' : self.deviceName}
            query_string = parse.urlencode( params ) 
            url = self.ipCatalog+ ':' +  self.portCatalog + '/getSchedules'
            url = url + "?" + query_string 

            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)
            self.bot.sendMessage(from_id, text="Schedule: \n start:" + data_dictHome[0]['startHour'] +",\n end:" +  data_dictHome[0]['endHour'])
            
            
            
        if(query_data == 'post_schedule_heating'):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Morning', callback_data='post_schedule_heating_morning')],
                    [InlineKeyboardButton(text='Afternoon', callback_data='post_schedule_heating_afternoon')],
                    [InlineKeyboardButton(text='Evening', callback_data='post_schedule_heating_evening')],
                    [InlineKeyboardButton(text='Night', callback_data='post_schedule_heating_night')],
                    [InlineKeyboardButton(text='AllDay', callback_data='post_schedule_heating_allday')]
                
                ])

            x = self.bot.sendMessage(from_id, 'Use the menu below', reply_markup=keyboard)
       

        #modifca fascia oraria in base alla scelta 
        if('post_schedule_heating' in query_data):

            modifica = query_data.split("_")[3]
            params = {
                'mod' : modifica}
            query_string = parse.urlencode( params ) 
            url = self.ipCatalog+ ':' +  self.portCatalog + '/getSchedules'
            url = url + "?" + query_string 
            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)


            json_data = json.dumps( {"schedules": [
            {
                "deviceName": self.deviceName,
                "startHour": data_dictHome[0][0]['startHour'],
                "endHour": data_dictHome[0][0]['endHour']
            }]})  
            params = {
                'room' : self.deviceName}
            query_string = parse.urlencode( params ) 
            url = self.ipCatalog+ ':' +  self.portCatalog + '/postSchedule'
            url = url + "?" + query_string 

            re = requests.post(url, 
                    data = json_data,
             )

            self.bot.sendMessage(from_id, text= "Schedule modified")
            

        if query_data == "newDevice":
            params = {
                'chatid' : self.from_id}    
            query_string = parse.urlencode( params ) 
            url = self.ipCatalog+ ':' +  self.portCatalog + '/getDevicesList' + "?" + query_string
            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            devices = json.loads(dataHome)

            reqHome = request.urlopen(self.ipCatalog+ ':' +  self.portCatalog + '/getChannels')
            dataHome = reqHome.read().decode('utf-8')
            channels = json.loads(dataHome)

            reqHome = request.urlopen(self.ipCatalog+ ':' +  self.portCatalog + '/getnDev')
            nDev = int(reqHome.read().decode('utf-8'))
                    

            flag = False
            for channel in channels: 
                if channel["status"] == "idle": 
                    dev = str(nDev + 1)
                    flag = True

            devices = []
            if flag:
                devices.append({
                "deviceName": "RoomSystem_" + dev,
                "deviceID": nDev + 1,
                "device": []
                })
                json_data = json.dumps( devices)
                
                params = {
                    'chatid' : self.from_id}
                query_string = parse.urlencode( params ) 
                url = self.ipCatalog+ ':' +  self.portCatalog + '/postAddDevice'
                url = url + "?" + query_string 

                re = requests.post(url, 
                        data = json_data,
                )

                self.bot.sendMessage(from_id, text='Device RoomSystem_' + dev + " successfully added")
            else: 
                self.bot.sendMessage(from_id, text="Out of channels")




        if('getHealth' in query_data):
            params = {  
                'chatid' : self.from_id}
            query_string = parse.urlencode( params ) 
            url = self.ipHealth + ':' +  self.portHealth + '/getHealth'
            url = url + "?" + query_string 

            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)

            for i, room in enumerate(data_dictHome):
                room = json.dumps(room)
                self.bot.sendMessage(from_id, text = room)

if __name__== "__main__":

    tg = TelegramClass()
    while 1:
        time.sleep(10)