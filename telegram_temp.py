from cgi import parse_header
import json
import logging
import sys
import time
from unicodedata import name
from matplotlib.font_manager import json_dump
import telepot
import urllib
from urllib import request
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import Home_Catalog as hc

import requests

class TelegramClass(object):

    def __init__(self,tokenBot):
        self.deviceName = ""
        self.tokenBot = tokenBot
        self.bot = telepot.Bot(self.tokenBot)

        MessageLoop(self.bot, {'chat': self.on_chat_message,
                'callback_query': self.on_callback_query}).run_as_thread()


    #la funzione on_chat_message crea una inline keyboard
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Temperature', callback_data='temp')],
                    [InlineKeyboardButton(text='Umidity', callback_data='umid')],
                    [InlineKeyboardButton(text='CO', callback_data='co')],
                    [InlineKeyboardButton(text='Schedule', callback_data='sched')],
                    [InlineKeyboardButton(text='Flame Aanalogo', callback_data='flameA')],
                    [InlineKeyboardButton(text='Flame Digitale', callback_data='flameD')]
                ])

        self.bot.sendMessage(chat_id, 'Usa il menu per mostrare i valori dela tua WeatherStation', reply_markup=keyboard)

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

        print('Callback Query:', query_id, from_id, query_data)

        if(query_data == 'temp'):
            self.bot.sendMessage(from_id, text='La Temperatura è di: ' + feeds[1]['field1'] + '°C')
            
        elif(query_data == 'umid'):
            self.bot.sendMessage(from_id, text="L'Umidità è il: " + feeds[1]['field2'] + '%')
            
        elif(query_data == 'co'):
            self.bot.sendMessage(from_id, text='La Pressione è di: ' + feeds[1]['field3'] + ' mbar')
            
        if query_data == "sched":
                buttons = [[InlineKeyboardButton(text=f'Roome number 1', callback_data=f'HeatingSystem_1'), 
                        InlineKeyboardButton(text=f'Room number 2', callback_data=f'HeatingSystem_2')]]
                keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                self.bot.sendMessage(from_id, text='Choose a room', reply_markup=keyboard)
          
        
        if('HeatingSystem' in query_data):
            
            self.deviceName = query_data 
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    # [InlineKeyboardButton(text='Visualizzare Schedule Riscaldamento', callback_data= deviceName)],
                    [InlineKeyboardButton(text='Visualizzare Schedule Riscaldamento', callback_data= 'get_schedule_heating')],
                    [InlineKeyboardButton(text='Modifica orario', callback_data='post_schedule_heating')]
                ])

            x = self.bot.sendMessage(from_id, 'Usa il menu per scegliere azione schedule', reply_markup=keyboard)
            

# non puù necessaria
        # if(query_data == "HeatingSystem_1"):
        #         reqHome = request.urlopen('http://127.0.0.1:8080/getSchedulesRoomOne')
        #         dataHome = reqHome.read().decode('utf-8')
        #         data_dictHome = json.loads(dataHome)
        #         print(data_dictHome)
        #         self.bot.sendMessage(from_id, text="Schedule room one: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
                
        # if(query_data == "HeatingSystem_2"):
        #         reqHome = request.urlopen('http://127.0.0.1:8080/getSchedulesRoomTwo')
        #         dataHome = reqHome.read().decode('utf-8')
        #         data_dictHome = json.loads(dataHome)
        #         self.bot.sendMessage(from_id, text= "You choose room number two")
                
              
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
        


        if(query_data == 'post_schedule_heating_morning'):

            json_data = json.dumps( {"schedules": [
            {
                "deviceName": "HeatingSystem_1",
                "startHour": "08:00:00",
                "endHour": "11:00:00"
            }]})  

            r = requests.post('http://127.0.0.1:8080/postSchedule', 
                    data=json_data,
                )
        
            self.bot.sendMessage(from_id, text= "Schedule modified")
            
            
        if(query_data == 'post_schedule_heating_afternoon'):
            reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)
            self.bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
            print(data_dictHome[0])
            
        if(query_data == 'post_schedule_heating_evening'):
            reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)
            self.bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
            print(data_dictHome[0])
            
        if(query_data == 'post_schedule_heating_night'):
            reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)
            self.bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
            print(data_dictHome[0])
            
        if(query_data == 'post_schedule_heating_allday'):
            reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
            dataHome = reqHome.read().decode('utf-8')
            data_dictHome = json.loads(dataHome)
            self.bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
            print(data_dictHome[0])

        # elif(query_data == 'flameA'):
        #     self.bot.sendMessage(from_id, text='Il sensore di luce misura: ' + feeds[1]['field5'] + ' di un range 0 -1024')

        # elif(query_data == 'flameD'):

        #     if(feeds[1]['field6'] == '0'):
        #         self.bot.sendMessage(from_id, text="Non c'è fiamma in casa")
        
        #     elif(feeds[1]['field6'] == '1'):
        #         self.bot.sendMessage(from_id, text="ATTENZIONE C'è PRESENZA DI FIAMMA IN CASA!")    

    #AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa
    # funzione che serve per impostare quale stanza usare

    #  def on_chat_message(self, msg):
    #         content_type, chat_type, chat_ID = telepot.glance(msg)
    #         message = msg['text']
    #         if message == "/switchon":
    #             payload = self.__message.copy()
    #             payload['e'][0]['v'] = "on"
    #             payload['e'][0]['t'] = time.time()
    #             self.client.myPublish(self.topic, payload)
    #             self.self.bot.sendMessage(chat_ID, text="Led switched on")   #if I write on telegram /switchOn the bot reply to me with 'on'
    #         elif message == "/switchOff":
    #             payload = self.__message.copy()
    #             payload['e'][0]['v'] = "off"
    #             payload['e'][0]['t'] = time.time()
    #             self.client.myPublish(self.topic, payload)
    #             self.self.bot.sendMessage(chat_ID, text="Led switched off")   #if I write on telegram /switchOff the bot reply to me with 'off'
    #         elif message == "/sayHello":
    #             self.self.bot.sendMessage(chat_ID, text="Hello")
    #         else:
    #             self.self.bot.sendMessage(chat_ID, text="Command not supported")


    # def on_chat_message(self, msg):
    #         content_type, chat_type, chat_ID = telepot.glance(msg)
    #         message = msg['text']
            

    # def on_callback_query(self,msg):
    #         query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')

            
    #         payload = self.__message.copy()
    #         payload['e'][0]['v'] = query_data
    #         payload['e'][0]['t'] = time.time()
    #         self.client.myPublish(self.topic, payload)
    #         self.self.bot.sendMessage(chat_ID, text=f"Led switched {query_data}")
    
        

if __name__== "__main__":

    # immagazzina il token per il got telegram renbot
    token = '5201662282:AAEdEc4GJQMrOEpTwXNtf8OgZ1rwfak4mhg'
    # bot = telepot.Bot(TOKEN)

    tg = TelegramClass(token)

    while 1:
        time.sleep(10)