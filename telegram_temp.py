from cgi import parse_header
# from curses.panel import bottom_panel
import json
import logging
import sys
import time
from turtle import update
from unicodedata import name
import threading
from matplotlib.font_manager import json_dump
import telepot
import urllib
from urllib import request
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# from telegram import Update
# from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
      

class TelegramClass(threading.Thread):
    class Co_control(threading.Thread):
        def __init__(self, fromID, bot):
            threading.Thread.__init__(self)
            self.from_id = fromID
            self.bot = bot

        def run(self):
            while(1):
                params = {
                    'room' : 'all'}
                query_string = urllib.parse.urlencode( params ) 
                url = 'http://127.0.0.1:8070/getCOstatus'
                url = url + "?" + query_string 

                reqHome = request.urlopen(url)
                dataHome = reqHome.read().decode('utf-8')
                if dataHome != 'False':
                    self.bot.sendMessage(self.from_id, text=dataHome)
                    
                time.sleep(180)

    def __init__(self,tokenBot):
        self.deviceName = ""
        self.tokenBot = tokenBot
        self.chatIDs = []
        self.bot = telepot.Bot(self.tokenBot)
        self.th_inf = "m"
        self.th_sup = "n"
        self.next = ""
        self.from_id = ""


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
        if message == "ciao":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Temperature', callback_data='temp')],
                [InlineKeyboardButton(text='Umidity', callback_data='umid')],
                [InlineKeyboardButton(text='Threshold', callback_data='threshold')],
                [InlineKeyboardButton(text='Schedule', callback_data='sched')],
                [InlineKeyboardButton(text='Add new device', callback_data='newDevice')],
                [InlineKeyboardButton(text='Comfort', callback_data='getComfort')],
                [InlineKeyboardButton(text='Control System Health', callback_data='getHealth')]
            ])

            self.bot.sendMessage(chat_id, 'Usa il menu per mostrare i valori dela tua WeatherStation', reply_markup=keyboard)

        elif message.split(" ")[0].isnumeric():
            self.th_inf = message.split(" ")[0]
            self.th_sup = message.split(" ")[1]
            if('modThreshold' in self.next):

                # self.bot.update.message.reply_text('What do you want to name this dog?')

                json_data = json.dumps( {"schedules": [
                {
                    "deviceName": self.deviceName,#TODO inserire soglia temp
                    "th_inf": self.th_inf,
                    "th_sup": self.th_sup
                }]})  
                params = {
                    'room' : self.deviceName}
                query_string = urllib.parse.urlencode( params ) 
                url = 'http://127.0.0.1:8080/postThreshold'
                url = url + "?" + query_string 

                re = requests.post(url, 
                        data = json_data,
                )

                self.th_inf = "m"
                self.th_sup = "n"

                self.bot.sendMessage(chat_id, text= "Thresholds modified")


    #la funzione on_callback_query processa i dati da Thingspeak e reagisce a seconda del pulsante premuto
        
    def on_callback_query(self, msg):
        # immagazzina in una variabile la risposta dal GET response

        response = request.urlopen('https://api.thingspeak.com/channels/1669938/feeds.json?api_key=4D9OPXEJK7T63SVN&results=2')

        # preleva i dati json dalla richiesta

        data = response.read().decode('utf-8')

        # convertiamo la stringa in dizionario

        data_dict = json.loads(data)

        #separiamo i valori che ci interessano

        feeds = data_dict['feeds']

        #facciamo reagire alla pressione del pulsante
        
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

        self.from_id = from_id

        print('Callback Query:', query_id, from_id, query_data)

        if(query_data == 'temp'):
            self.bot.sendMessage(from_id, text='La Temperatura è di: ' + feeds[1]['field1'] + '°C')
            
        elif(query_data == 'umid'):
            self.bot.sendMessage(from_id, text="L'Umidità è il: " + feeds[1]['field2'] + '%')
            
        elif(query_data == 'co'):
            self.bot.sendMessage(from_id, text='La Pressione è di: ' + feeds[1]['field3'] + ' mbar')
            
        if query_data == "sched" or query_data == "getComfort" or query_data == "threshold":
            self.utility = query_data
            reqHome = request.urlopen('http://127.0.0.1:8080/getDevicesList')
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
                        # [InlineKeyboardButton(text='Visualizzare Schedule Riscaldamento', callback_data= deviceName)],
                        [InlineKeyboardButton(text='Visualizzare Schedule Riscaldamento', callback_data= 'get_schedule_heating')],
                        [InlineKeyboardButton(text='Modifica orario', callback_data='post_schedule_heating')]
                    ])

                x = self.bot.sendMessage(from_id, 'Usa il menu per scegliere azione schedule', reply_markup=keyboard)
            elif self.utility == "getComfort":
                params = {
                    'room' : self.deviceName}
                query_string = urllib.parse.urlencode( params ) 
                url = 'http://127.0.0.1:8070/getComfort'
                url = url + "?" + query_string 

                reqHome = request.urlopen(url)
                dataHome = reqHome.read().decode('utf-8')
                # data_dictHome = json.loads(dataHome)

                self.bot.sendMessage(from_id, text = dataHome)

            elif self.utility == "threshold":
                params = {
                    'room' : self.deviceName}
                query_string = urllib.parse.urlencode( params ) 
                url = 'http://127.0.0.1:8080/getThreshold'
                url = url + "?" + query_string 

                reqHome = request.urlopen(url)
                dataHome = reqHome.read().decode('utf-8')
                # data_dictHome = json.loads(dataHome)

                self.bot.sendMessage(from_id, text = dataHome)

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        # [InlineKeyboardButton(text='Visualizzare Schedule Riscaldamento', callback_data= deviceName)],
                        [InlineKeyboardButton(text='Modify thresholds heating system', callback_data= 'modThresholdMess')],
                        [InlineKeyboardButton(text='Exit', callback_data='exit')] # TODO
                    ])
                
                x = self.bot.sendMessage(from_id, 'Usa il menu per scegliere azione schedule', reply_markup=keyboard)
                

        if('modThresholdMess' in query_data):

            self.bot.sendMessage(from_id, text= "Insert threshold separated by a white space. Like '15 21':")
            self.next = "modThreshold"
                  
              
        if(query_data == 'get_schedule_heating'):
            params = {
                'room' : self.deviceName}
            query_string = urllib.parse.urlencode( params ) 
            url = 'http://127.0.0.1:8080/getSchedules'
            url = url + "?" + query_string 

            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)
            self.bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
            
            
            
        if(query_data == 'post_schedule_heating'):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Morning', callback_data='post_schedule_heating_morning')],
                    [InlineKeyboardButton(text='Afternoon', callback_data='post_schedule_heating_afternoon')],
                    [InlineKeyboardButton(text='Evening', callback_data='post_schedule_heating_evening')],
                    [InlineKeyboardButton(text='Night', callback_data='post_schedule_heating_night')],
                    [InlineKeyboardButton(text='AllDay', callback_data='post_schedule_heating_allday')]
                
                ])

            x = self.bot.sendMessage(from_id, 'Usa il menu per scegliere azione schedule', reply_markup=keyboard)
       

        #modifca fascia oraria in base alla scelta 
        if('post_schedule_heating' in query_data):

            modifica = query_data.split("_")[3]
            params = {
                'mod' : modifica}
            query_string = urllib.parse.urlencode( params ) 
            url = 'http://127.0.0.1:8080/getSchedules'
            url = url + "?" + query_string 
            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)


            json_data = json.dumps( {"schedules": [
            {
                "deviceName": self.deviceName,#TODO inserire soglia temp
                "startHour": data_dictHome[0][0]['startHour'],
                "endHour": data_dictHome[0][0]['endHour']
            }]})  
            params = {
                'room' : self.deviceName}
            query_string = urllib.parse.urlencode( params ) 
            url = 'http://127.0.0.1:8080/postSchedule'
            url = url + "?" + query_string 

            re = requests.post(url, 
                    data = json_data,
             )

            self.bot.sendMessage(from_id, text= "Schedule modified")
            

        if query_data == "newDevice":
            reqHome = request.urlopen('http://127.0.0.1:8080/getDevicesList')
            dataHome = reqHome.read().decode('utf-8')
            devices = json.loads(dataHome)
        
            dev = str(len(devices)+1)
            if int(dev) <= 3:  
                devices.append({
                "deviceName": "RoomSystem_" + dev,
                "device": []
                })


                json_data = json.dumps( devices)

                url = 'http://127.0.0.1:8080/postAddDevice'

                re = requests.post(url, 
                        data = json_data,
                )

                self.bot.sendMessage(from_id, text='Device n ' + dev + " successfully added")
            else: 
                self.bot.sendMessage(from_id, text="Out of channels")




        if('getHealth' in query_data):

            url = 'http://127.0.0.1:8050/getHealth'

            reqHome = request.urlopen(url)
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)
            for i, room in enumerate(data_dictHome):
                room = json.dumps(room)
                self.bot.sendMessage(from_id, text = room)



if __name__== "__main__":

    # immagazzina il token per il got telegram renbot
    token = '5201662282:AAEdEc4GJQMrOEpTwXNtf8OgZ1rwfak4mhg'
    # bot = telepot.Bot(TOKEN)

    tg = TelegramClass(token)

    while 1:
        time.sleep(10)