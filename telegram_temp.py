import json
import logging
import sys
import time
import telepot
from urllib import request
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import Home_Catalog as hc

# immagazzina il token per il got telegram renbot

TOKEN = '5201662282:AAEdEc4GJQMrOEpTwXNtf8OgZ1rwfak4mhg'

#creiamo tutte le funzioni necessarie al funzionamento del bot

#la funzione on_chat_message crea una inline keyboard

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Temperature', callback_data='temp')],
                   [InlineKeyboardButton(text='Umidity', callback_data='umid')],
                   [InlineKeyboardButton(text='CO', callback_data='co')],
                   [InlineKeyboardButton(text='Schedule', callback_data='sched')],
                   [InlineKeyboardButton(text='Flame Aanalogo', callback_data='flameA')],
                   [InlineKeyboardButton(text='Flame Digitale', callback_data='flameD')]
               ])

    bot.sendMessage(chat_id, 'Usa il menu per mostrare i valori dela tua WeatherStation', reply_markup=keyboard)

#la funzione on_callback_query processa i dati da Thingspeak e reagisce a seconda del pulsante premuto
    
def on_callback_query(msg):
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
        bot.sendMessage(from_id, text='La Temperatura è di: ' + feeds[1]['field1'] + '°C')
        
    elif(query_data == 'umid'):
        bot.sendMessage(from_id, text="L'Umidità è il: " + feeds[1]['field2'] + '%')
        
    elif(query_data == 'co'):
        bot.sendMessage(from_id, text='La Pressione è di: ' + feeds[1]['field3'] + ' mbar')

    # elif(query_data == 'flameA'):
    #     bot.sendMessage(from_id, text='Il sensore di luce misura: ' + feeds[1]['field5'] + ' di un range 0 -1024')

    # elif(query_data == 'flameD'):

    #     if(feeds[1]['field6'] == '0'):
    #         bot.sendMessage(from_id, text="Non c'è fiamma in casa")
    
    #     elif(feeds[1]['field6'] == '1'):
    #         bot.sendMessage(from_id, text="ATTENZIONE C'è PRESENZA DI FIAMMA IN CASA!")    


    if(query_data == 'sched'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Visualizzare Schedule Riscaldamento', callback_data='get_schedule_heating')],
                [InlineKeyboardButton(text='Modifica orario', callback_data='post_schedule_heating')]
            ])

        x = bot.sendMessage(from_id, 'Usa il menu per scegliere azione schedule', reply_markup=keyboard)


    if(query_data == 'get_schedule_heating'):
        reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
        dataHome = reqHome.read().decode('utf-8')
        data_dictHome = json.loads(dataHome)
        bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
        print(data_dictHome[0])
        
    if(query_data == 'post_schedule_heating'):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Morning', callback_data='post_schedule_heating_morning')],
                [InlineKeyboardButton(text='Afternoon', callback_data='post_schedule_heating_afternoon')]
                [InlineKeyboardButton(text='Evening', callback_data='post_schedule_heating_evening')],
                [InlineKeyboardButton(text='Night', callback_data='post_schedule_heating_night')]
            ])

        x = bot.sendMessage(from_id, 'Usa il menu per scegliere azione schedule', reply_markup=keyboard)
        
    if(query_data == 'post_schedule_heating_morning'):
        reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
        dataHome = reqHome.read().decode('utf-8')
        data_dictHome = json.loads(dataHome)
        bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
        print(data_dictHome[0])
        
    if(query_data == 'post_schedule_heating_afternoon'):
        reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
        dataHome = reqHome.read().decode('utf-8')
        data_dictHome = json.loads(dataHome)
        bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
        print(data_dictHome[0])
        
    if(query_data == 'post_schedule_heating_evening'):
        reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
        dataHome = reqHome.read().decode('utf-8')
        data_dictHome = json.loads(dataHome)
        bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
        print(data_dictHome[0])
        
    if(query_data == 'post_schedule_heating_night'):
        reqHome = request.urlopen('http://127.0.0.1:8080/schedules')
        dataHome = reqHome.read().decode('utf-8')
        data_dictHome = json.loads(dataHome)
        bot.sendMessage(from_id, text="Schedule: /n start:" + data_dictHome[0]['startHour'] +",/n end:" +  data_dictHome[0]['endHour'])
        print(data_dictHome[0])
       
        
        
#inizializziamo le funzioni


bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

while 1:
    time.sleep(10)