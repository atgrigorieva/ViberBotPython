from flask import Flask, request, Response
import flask_restful

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from viberbot.api.messages.url_message import URLMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.event_type import EventType


import time
import logging
import sched
import threading
import os
import locale

locale.setlocale(locale.LC_ALL, '')

import psycopg2
from psycopg2 import sql
from datetime import date, datetime, timedelta

import json


#Логи для бота
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('viber bot.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


app = Flask(__name__)
api = flask_restful.Api(app)
'''@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"'''


TOKEN = '49cc42b11a27d0ba-ccb237ef23e7f055-26665b55f3ebb019'
webhookURL = 'https://ecoviewapp.fvds.ru/'

viber = Api(BotConfiguration(
    name='ПЭЛ-помощник',
    avatar='',
    auth_token=TOKEN
))

text_command = ""
select_category = False
OUTPUT_ = {
    'mass': []
}
OUTPUT = {
    'mass': []
}
name_razdel = ""

@app.route('/', methods=["POST"])
def incoming():
    #global output_
    logger.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        print("durak")
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())

    #viber.post_messages_to_public_account(sender=viber_request.get_sender().get_id(),
     #                                     messages=[TextMessage(text="sample message")])

    if isinstance(viber_request, ViberConversationStartedRequest):
        viber.send_messages(viber_request.sender.id, [
            TextMessage(text="Добрый день!\n Для начала работы с ботом наберите Начать.")
        ])


    if isinstance(viber_request, ViberMessageRequest):
        #message = viber_request.message

        SAMPLE_BUTTON = {
            "Type": "keyboard",
            "InputFieldState": "hidden",
            "Buttons": [

                {
                    "Columns": 3,
                    "Rows": 1,
                    "ActionBody": "_bot_product",
                    "Text": '<font color="#f5f8f6"><b>Продукция</b></font>',
                    "Silent": "true",
                    "BgColor": "#015b29",
                    "TextSize": "large",
                    "TextHAlign": "center",
                    "TextVAlign": "middle",
                    "ActionType": "reply",
                    "Image":  webhookURL + "images/png/shoppaymentorderbuy-250_90_5.png",
                    #"ImageScaleType":"fit"
                    # "BgMediaType": "picture",
                    # "ImageScaleType": "fit",
                    # "BgMediaScaleType": "fit",
                },


                {
                    "Columns": 3,
                    "Rows": 1,
                    "ActionBody": "_bot_search",
                    "Text": '<font color="#f5f8f6"><b>Поиск</b></font>',
                    "BgColor": "#015b29",
                    "TextSize": "large",
                    "TextHAlign": "center",
                    "TextVAlign": "middle",
                    "ActionType": "reply",
                     "Image": webhookURL + "images/png/search_find_magnifyingglass_15640_4.png"

                }
            ]
        }

        RETURNBUTTON = {
                            "Type": "keyboard",
                            "InputFieldState": "hidden",
                            "Buttons": [{
                                "Columns": 6,
                                "Rows": 1,
                                "ActionBody": "_bot_home",
                                "Text": "В главное меню",
                                "Silent": "true",
                                "BgColor": "#015b29",
                                "TextSize": "large",
                                "TextHAlign": "center",
                                "TextVAlign": "middle",
                                "ActionType": "reply",
                            }]
                    }

        SEARCHBUTTON = {
                            "Type": "keyboard",
                            "InputFieldState": "hidden",
                            "Buttons": [
                                {
                                    "Columns": 3,
                                    "Rows": 1,
                                    "ActionBody": "_bot_search_articul",
                                    "Text": '<font color="#f5f8f6"><b>Поиск по артикулу</b></font>',
                                    "Silent": "true",
                                    "BgColor": "#015b29",
		                            "TextSize": "large",
                                },
                                {
                                    "Columns": 3,
                                    "Rows": 1,
                                    "ActionBody": "_bot_search_product",
                                    "Text": '<font color="#f5f8f6"><b>Поиск по названию</b></font>',
                                    "Silent": "true",
                                    "BgColor": "#015b29",
		                            "TextSize": "large",
                                },

                                {
                                    "Columns": 6,
                                    "Rows": 1,
                                    "ActionBody": "_bot_home",
                                    "Text": '<font color="#f5f8f6"><b>В главное меню</b></font>',
                                    "Silent": "true",
                                    "BgColor": "#015b29",
                                    "TextSize": "large",
                                    "TextHAlign": "center",
                                    "TextVAlign": "middle",
                                    "ActionType": "reply",
                                    "Image": webhookURL + "images/png/home256_24783_3.png",
                                }
                            ]
                    }

        STILLBUTTON = """{
                "Type": "keyboard",
                "InputFieldState": "hidden",
                "Buttons": [{
                "Columns": 6,
                "Rows": 1,
                "ActionBody": "_bot_search_still",
                "Text": "Еще",
                "Silent": "true",
                 "BgColor": "#015b29"
                 },
                 {
                 "Columns": 6,
                 "Rows": 1,
                 "ActionBody": "_bot_home",
                 "Text": "В главное меню",
                 "Silent": "true",
                        "BgColor": "#015b29",
                                "TextSize": "large",
                                "TextHAlign": "center",
                                "TextVAlign": "middle",
                                "ActionType": "reply",
              
              }]
         }"""

        message = viber_request.message
        command = message.text


        if command == "Начать" or command == "начать":
            viber.send_messages(viber_request.sender.id, [
                TextMessage(
                    text='Могу рассказать Вам о наличии товаров на складах и действующих ценах и акциях.\n\n"Продукция" - переход в каталог товаров.\n"Поиск" - поиск по артикулу или наименованию.\n\nВыберите, пожалуйста, подходящий пункт меню.'),
                KeyboardMessage(keyboard=SAMPLE_BUTTON, min_api_version=6)
            ])
            #del OUTPUT_['mass'][:]
            #del OUTPUT['mass'][:]

        if command == "_bot_search":
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text="Выберите параметры поиска"), KeyboardMessage(keyboard=SEARCHBUTTON)
            ])

        if command == "_bot_home":
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text='Могу рассказать Вам о наличии товаров на складах и действующих ценах и акциях.\n\n"Продукция" - переход в каталог товаров.\n"Поиск" - поиск по артикулу или наименованию.\n\nВыберите, пожалуйста, подходящий пункт меню.'),
                KeyboardMessage(keyboard=SAMPLE_BUTTON)
            ])
            #del OUTPUT_['mass'][:]
          #  del OUTPUT['mass'][:]

        if command == "_bot_search_articul":
            global text_command
            text_command = "_bot_search_articul"
           # del OUTPUT['mass'][:]
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text="Введите артикул для поиска. Не менее 4-х символов"), KeyboardMessage(keyboard=SEARCHBUTTON)
            ])
        if command == "_bot_search_product":
            text_command = "_bot_search_product"
            #del OUTPUT['mass'][:]
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text="Введите название или часть названия"), KeyboardMessage(keyboard=SEARCHBUTTON)
            ])

        if text_command == "_bot_search_articul" and not(command.startswith("_")):
            text_command = "_bot_search_articul"
            # print(text_command)
            message = viber_request.message
            #del OUTPUT['mass'][:]
            if len(str(message.text)) >= 4:
                # conn = psycopg2.connect(dbname='test-pe-lab', user='postgreadmin',password='5112274', host='78.24.216.107', port=5433)
                conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin', password='5112274',
                                        host='78.24.216.107', port=5433)

                with conn.cursor() as cursor:
                    stmt = sql.SQL(
                        "Select products.id_product, products.articul, prices.price, quantities.quantity, products.product, prices.time_, products.link, products.image, prices.stock_price FROM products LEFT JOIN prices on products.id_product = prices.id_product and prices.date_ = current_date LEFT JOIN quantities on products.id_product = quantities.id_product and quantities.date_ = current_date WHERE articul ~* %s")

                    cursor.execute(stmt, [message.text])
                    #global output

                    outputProduct = cursor.fetchall()

                    data = {
                        "Type": "rich_media",
                        "ButtonsGroupColumns": 6,
                        "ButtonsGroupRows": 7,
                        # "BgColor": "#E6E6FA",
                        "Buttons": [
                        ]
                    }

                    if len(outputProduct) == 0 and command != text_command:
                        viber.send_messages(viber_request.sender.id, [
                            TextMessage(text="По вашему запросу ничего не найдено."),
                            KeyboardMessage(keyboard=SEARCHBUTTON)
                        ])
                    countProduct = len(outputProduct)

                    if len(outputProduct) <= 3:
                        lenOut = len(outputProduct)
                    else:
                        lenOut = 3

                    for number in range(0, len(outputProduct), 1):
                        if outputProduct != None:
                            for row in outputProduct[:lenOut]:
                                dataAppend(row, data)

                        if len(data["Buttons"]) > 0:
                            #output_.clear()
                            #global output_
                            del outputProduct[:lenOut]

                            if len(outputProduct) == 0:
                                outputProduct = None
                            #output_ = output[:]
                            '''if len(OUTPUT['mass']) > 0:
                                viber.send_messages(viber_request.sender.id,
                                                    [RichMediaMessage(rich_media=data, min_api_version=6),
                                                     KeyboardMessage(keyboard=json.loads(STILLBUTTON))])
                            else:'''
                            viber.send_messages(viber_request.sender.id,
                                                    [RichMediaMessage(rich_media=data, min_api_version=6)
                                                     ])

                        data = {
                            "Type": "rich_media",
                            "ButtonsGroupColumns": 6,
                            "ButtonsGroupRows": 7,
                            # "BgColor": "#E6E6FA",
                            "Buttons": [
                            ]
                        }

                    if outputProduct == None:
                        if countProduct > 0:
                            viber.send_messages(viber_request.sender.id,
                                                [TextMessage(text="Всего найдено товаров: " + str(countProduct) + " (смотри выше 👆)"),
                                                 KeyboardMessage(keyboard=SEARCHBUTTON)])



        if text_command == "_bot_search_product" and not(command.startswith("_")):
            text_command = "_bot_search_product"

            message = viber_request.message

            if len(str(message.text)) >= 4:
                # conn = psycopg2.connect(dbname='test-pe-lab', user='postgreadmin',password='5112274', host='78.24.216.107', port=5433)
                conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin', password='5112274',
                                        host='78.24.216.107', port=5433)

                with conn.cursor() as cursor:
                    stmt = sql.SQL(
                        "Select products.id_product, products.articul, prices.price, quantities.quantity, products.product, prices.time_, products.link, products.image, prices.stock_price FROM products LEFT JOIN prices on products.id_product = prices.id_product and prices.date_ = current_date LEFT JOIN quantities on products.id_product = quantities.id_product and quantities.date_ = current_date WHERE product ~* %s")

                    cursor.execute(stmt, [message.text])
                    outputProduct = cursor.fetchall()

                    data = {
                        "Type": "rich_media",
                        "ButtonsGroupColumns": 6,
                        "ButtonsGroupRows": 7,
                        # "BgColor": "#E6E6FA",
                        "Buttons": [
                        ]
                    }

                    if len(outputProduct) == 0 and command != text_command:
                        viber.send_messages(viber_request.sender.id, [
                            TextMessage(text="По вашему запросу ничего не найдено."),
                            KeyboardMessage(keyboard=SEARCHBUTTON)
                        ])

                    countProduct = len(outputProduct)
                    if len(outputProduct) <= 3:
                        lenOut = len(outputProduct)
                    else:
                        lenOut = 3

                    for number in range(0, len(outputProduct), 1):
                        if outputProduct != None:
                            for row in outputProduct[:lenOut]:
                                dataAppend(row, data)
                        if len(data["Buttons"]) > 0:

                            del outputProduct[:lenOut]

                            logger.debug("text_command == '_bot_search_product' OUTPUT['mass'] =: " + str(len(outputProduct)))

                            if len(outputProduct) == 0:
                                outputProduct = None
                            '''if len(OUTPUT['mass']) > 0:
                                viber.send_messages(viber_request.sender.id,
                                                    [RichMediaMessage(rich_media=data, min_api_version=6),
                                                     KeyboardMessage(keyboard=json.loads(STILLBUTTON))])
                            else:'''
                            viber.send_messages(viber_request.sender.id,
                                                    [RichMediaMessage(rich_media=data, min_api_version=6)
                                                     ])
                        data = {
                            "Type": "rich_media",
                            "ButtonsGroupColumns": 6,
                            "ButtonsGroupRows": 7,
                            # "BgColor": "#E6E6FA",
                            "Buttons": [
                            ]
                        }

                    if outputProduct == None:
                        viber.send_messages(viber_request.sender.id,
                                            [TextMessage(text="Всего найдено товаров: " + str(countProduct) + " (смотри выше 👆)"),
                                             KeyboardMessage(keyboard=SEARCHBUTTON)])

        if command == "_bot_search_still":
            text_command = "_bot_search_still"

            #output = OUTPUT_['mass'][:]
            #del output_[:]
            data = {
                "Type": "rich_media",
                "ButtonsGroupColumns": 6,
                "ButtonsGroupRows": 7,
                # "BgColor": "#E6E6FA",
                "Buttons": [
                ]
            }
            if len(OUTPUT['mass']) <= 3:
                lenOut = len(OUTPUT['mass'])
            else:
                lenOut = 3

            logger.debug("сommand == '_bot_search_still' OUTPUT['mass'] =: " + str(len(OUTPUT['mass'])))

            for row in OUTPUT['mass'][:lenOut]:
                dataAppend(row, data)
            if len(data["Buttons"]) > 0:
                #global output_
                #del OUTPUT_['mass'][:]
               # global output_
                #nonlocal output
                del OUTPUT['mass'][:lenOut]
                #OUTPUT_['mass'] = output[:]
                logger.debug("сommand == '_bot_search_still' OUTPUT['mass'] =: " + str(len(OUTPUT['mass'])))
                if len(OUTPUT['mass']) > 0:
                    viber.send_messages(viber_request.sender.id,
                                        [RichMediaMessage(rich_media=data, min_api_version=6),
                                         KeyboardMessage(keyboard=STILLBUTTON)])
                else:
                    viber.send_messages(viber_request.sender.id,
                                        [RichMediaMessage(rich_media=data, min_api_version=6),
                                         KeyboardMessage(keyboard=SEARCHBUTTON)])

        if command == "_bot_product":
            text_command = "_bot_product"

            conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin', password='5112274',
                                    host='78.24.216.107', port=5433)

            with conn.cursor() as cursor:
                smtp = sql.SQL("Select id_start_category, name_start_category From start_categories")
                cursor.execute(smtp)

                output = cursor.fetchall()
                categories_buttons = {
                    "Type": "keyboard",
                    "InputFieldState": "hidden",
                    "Buttons": []
                }
                for row in output:
                    categories_buttons["Buttons"].append({
                        "Columns": 3,
                        "Rows": 1,
                        "ActionType": "",
                        "ActionBody": row[1],
                        "Text": '<font color="#f5f8f6"><b>' + row[1].replace(" ", "\n") + '</b></font>',
                        "Silent": "true",
                        "BgColor": "#015b29",
		                            "TextSize": "large",
                        #"name": row[1]
                    })

                categories_buttons["Buttons"].append(
                    {
                    "Columns": 6,
                    "Rows": 1,
                    "ActionBody": "_bot_home",
                    "Text": '<font color="#f5f8f6"><b>В главное меню</b></font>',
                    "Silent": "true",
                    "BgColor": "#015b29",
                    "TextSize": "large",
                    "TextHAlign": "center",
                    "TextVAlign": "middle",
                    "ActionType": "reply",
                    "Image": webhookURL + "images/png/home256_24783_3.png",
                })
                viber.send_messages(viber_request.sender.id, [
                    TextMessage(text="Выберите, пожалуйста, из меню информация о каком товаре Вам нужна."),
                    KeyboardMessage(keyboard=categories_buttons)
                ])
        if command == "Общелабораторное оборудование" or command == "Аксессуары":
            message = viber_request.message
            global name_razdel
            name_razdel = message.text
            conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin', password='5112274',
                                    host='78.24.216.107', port=5433)

            with conn.cursor() as cursor:
                stmt = sql.SQL(
                    "Select start_categories.id_start_category, categories.id_category, categories.name_category From start_categories Left Join categories On start_categories.id_start_category = categories.id_start_category Where start_categories.name_start_category ~ %s")
                cursor.execute(stmt, [message.text])
                output = cursor.fetchall()
                data = {
                    "Type": "rich_media",
                    "ButtonsGroupColumns": 6,
                    "ButtonsGroupRows": 7,
                    # "BgColor": "#E6E6FA",
                    "Buttons": [
                    ]
                }

                for row in output:
                    data["Buttons"].append({
                        "Columns": 6,
                        "Rows": 1,
                        "Text": '<font color="#3c38d8"><u>' + row[2] + "</u></font>",
                        "ActionBody": row[2],
                        "TextVAlign": "middle",
                        "TextHAlign": "left",
                        "TextShouldFit": "true",
                        "Silent": "true",
                    })

            conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin', password='5112274',
                                    host='78.24.216.107', port=5433)

            with conn.cursor() as cursor:
                smtp = sql.SQL("Select id_start_category, name_start_category From start_categories")
                cursor.execute(smtp)

                output = cursor.fetchall()
                categories_buttons = {
                    "Type": "keyboard",
                    "InputFieldState": "hidden",
                    "Buttons": []
                }
                for row in output:
                    categories_buttons["Buttons"].append({
                        "Columns": 3,
                        "Rows": 1,
                        "ActionBody": row[1],
                        "Text": '<font color="#f5f8f6"><b>' + row[1] + '</b></font>',
                        "Silent": "true",
                        "BgColor": "#015b29",
		                            "TextSize": "large",
                    })

                categories_buttons["Buttons"].append(

                    {
                        "Columns": 6,
                        "Rows": 1,
                        "ActionBody": "_bot_home",
                        "Text": '<font color="#f5f8f6"><b>В главное меню</b></font>',
                        "Silent": "true",
                        "BgColor": "#015b29",
                        "TextSize": "large",
                        "TextHAlign": "center",
                        "TextVAlign": "middle",
                        "ActionType": "reply",
                        "Image": webhookURL + "images/png/home256_24783_3.png",
                })

            viber.send_messages(viber_request.sender.id, [RichMediaMessage(rich_media=data, min_api_version=6),
                                                          TextMessage(text="Выберите нужный раздел из списка выше."),
                                                          KeyboardMessage(keyboard=categories_buttons)])

        if command == "_bot_order_product":
            pass

        else:
            if command != "":

                message = viber_request.message

                conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin', password='5112274',

                                        host='78.24.216.107', port=5433)

                with conn.cursor() as cursor:

                    stmt = sql.SQL(

                        "Select start_categories.id_start_category, categories.id_category, categories.name_category From start_categories Left Join categories On start_categories.id_start_category = categories.id_start_category Where start_categories.name_start_category ~ %s")

                    cursor.execute(stmt, [name_razdel])

                    output = cursor.fetchall()

                    for row in output:

                        if command == row[2]:

                            stmt = sql.SQL(
                                "Select products.id_product, products.articul, prices.price, quantities.quantity, products.product, prices.time_, products.link, products.image, prices.stock_price  FROM products LEFT JOIN prices on products.id_product = prices.id_product and prices.date_ = current_date LEFT JOIN quantities on products.id_product = quantities.id_product and quantities.date_ = current_date Left Join categories On products.id_category = categories.id_category WHERE categories.name_category ~ %s")

                            cursor.execute(stmt, [message.text])

                            outputProduct = cursor.fetchall()

                            data = {

                                "Type": "rich_media",

                                "ButtonsGroupColumns": 6,

                                "ButtonsGroupRows": 7,

                                # "BgColor": "#E6E6FA",

                                "Buttons": [

                                ]

                            }

                            countProduct = len(outputProduct)
                            if len(outputProduct) <= 3:

                                lenOut = len(outputProduct)

                            else:

                                lenOut = 3

                            for number in range(0, len(outputProduct), 1):

                                if outputProduct != None:

                                    for row_ in outputProduct[:lenOut]:
                                        dataAppend(row_, data)

                                    if len(data["Buttons"]) > 0:

                                        # del outputProduct[:lenOut]

                                        for row_ in outputProduct[:lenOut]:
                                            outputProduct.remove(row_)

                                        # time.sleep(1)

                                        if len(outputProduct) <= 3 and len(outputProduct) != 0:

                                            lenOut = len(outputProduct)

                                        else:

                                            lenOut = 3

                                        logger.debug(

                                            "text_command == '_bot_search_product' OUTPUTProduct['mass'] =: " + str(

                                                len(outputProduct)))

                                        if len(outputProduct) == 0:
                                            outputProduct = None



                                        viber.send_messages(viber_request.sender.id,
                                                            [RichMediaMessage(rich_media=data, min_api_version=6)])

                                    data = {

                                        "Type": "rich_media",

                                        "ButtonsGroupColumns": 6,

                                        "ButtonsGroupRows": 7,

                                        # "BgColor": "#E6E6FA",

                                        "Buttons": [

                                        ]

                                    }

                                else:
                                    command = None
                                    text_command = None
                                    name_razdel = None
                                    break

                            if outputProduct == None:

                                smtp = sql.SQL(

                                    "Select id_start_category, name_start_category From start_categories")

                                cursor.execute(smtp)

                                outputStartCat = cursor.fetchall()

                                categories_buttons = {

                                    "Type": "keyboard",

                                    "InputFieldState": "hidden",

                                    "Buttons": []

                                }

                                for row__ in outputStartCat:
                                    categories_buttons["Buttons"].append({

                                        "Columns": 3,

                                        "Rows": 1,

                                        "ActionBody": row__[1],

                                        "Text": '<font color="#f5f8f6"><b>' + row__[1] + '</b></font>',

                                        "Silent": "true",
                                        "BgColor": "#015b29",
		                            "TextSize": "large",

                                    })

                                categories_buttons["Buttons"].append(
                                    {

                                        "Columns": 6,

                                        "Rows": 1,

                                        "ActionBody": "_bot_home",

                                        "Text": '<font color="#f5f8f6"><b>В главное меню</b></font>',

                                        "Silent": "true",
                                        "BgColor": "#015b29",
                                        "TextSize": "large",
                                        "TextHAlign": "center",
                                        "TextVAlign": "middle",
                                        "ActionType": "reply",
                                        "Image": webhookURL + "images/png/home256_24783_3.png",

                                })

                                viber.send_messages(viber_request.sender.id,
                                                    [TextMessage(text="Всего товаров: " + str(countProduct) + " (смотри выше 👆)"),
                                                     KeyboardMessage(keyboard=categories_buttons)])

                        #return

    return Response(status=200)


def create_webhook(viber, webhookURL):
    print("hello")
    viber.set_webhook(webhookURL)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1>"


def dataAppend(row, data):
    if row[8] != None:
        stockPrice = str(locale.format('%.2f', row[8], grouping=True)).replace(",", ".") + " руб."
    else:
        stockPrice = "не проводится"

    if row[2] != None and row[2] != 0:
        price = str(locale.format('%.2f', row[2], grouping=True)).replace(",", ".") + " руб."
    else:
        price = "по запросу"

    if row[3] == None:
        sclad = str("нет в наличии")
    else:
        if row[3] <= 2:
            sclad = str(row[3])
        if row[3] > 2 and row[3] <= 5:
            sclad = "меньше 5"
        if row[3] > 5 and row[3] <= 10:
            sclad = "меньше 10"
        if row[3] > 10:
            sclad = "больше 10"


    if row[6] == None:
        url = ""
    else:
        url = str(row[6])

    if row[5] == None:
        datetime = ""
    else:
        datetime = str(row[5].strftime("%d.%m.%Y %H:%M"))

    if row[7] == None:
        pict = ""
    else:
        pict = str(row[7])
    data["Buttons"].append({
        "Columns": 4,
        "Rows": 3,
        "Text": '<font color="#323232" size="2"><b>Артикул: ' + row[1] + ",<br>" + row[4] + "</b></font>" + '<font color="#777777" size="2"><br>Цена: </font><font color="#6fc133" size="2">' + str(price) + "</font>",
        "ActionType": "open-url",
        "ActionBody": "https://ulabrus.ru" + url,
        # "TextSize": "medium",
        "TextVAlign": "middle",
        "TextHAlign": "left",
        "TextShouldFit": "true",
        "Silent": "true"

    })
    data["Buttons"].append({
        "Columns": 2,
        "Rows": 3,
        "BgMedia": "https://ulabrus.ru" + pict,
        "BgMediaType": "picture",
        # "ImageScaleType": "fit",
        "BgMediaScaleType": "fit",
        "ActionType": "open-url",
        "ActionBody": "https://ulabrus.ru" + url,
        "Silent": "true"
    })
    data["Buttons"].append({
        "Columns": 6,
        "Rows": 1,
        "Text": '<font color="#f41424" size="2">Цена по акции: </font><font color="#6fc133" size="2">' + stockPrice + '</font><font color="#777777" size="2"><br>На складе: </font><font color="#6fc133" size="2">' + str(sclad) + "</font>",
        "ActionType": "open-url",
        "ActionBody": "https://ulabrus.ru" + url,
        "TextSize": "medium",
        "TextVAlign": "middle",
        "TextHAlign": "left",
        "Silent": "true"
    })
    data["Buttons"].append({
        "Columns": 6,
        "Rows": 2,
        "Text": "<font color=#777777>Данные актуальны на: </font><font color=#6fc133>" + str(datetime) + "</font><font color=#777777><br>Цены указаны с учетом НДС 20%</font>",
        "ActionType": "open-url",
        "ActionBody": "https://ulabrus.ru" + url,
        "TextSize": "medium",
        "TextVAlign": "middle",
        "TextHAlign": "left",
        "Silent": "true"
    })
    data["Buttons"].append(
        {
            "Columns": 6,
            "Rows": 1,
            "ActionType": "open-url",
            "ActionBody": "https://ulabrus.ru" + url,
            "Text": '<font color="#8367db"><b>ПОДРОБНЕЕ</b></font>',
            "TextSize": "small",
            "TextVAlign": "middle",
            "TextHAlign": "middle",
            "Silent": "true"
        }
    )
    '''data["Buttons"].append(
        {
            "Columns": 3,
            "Rows": 1,
            "ActionType": "reply",
            "ActionBody": "_bot_order_product",
            "Text": '<font color="#8367db"><b>ЗАКАЗАТЬ</b></font>',
            "TextSize": "small",
            "TextVAlign": "middle",
            "TextHAlign": "middle",
            "Silent": "true"
        }
    )'''

if __name__ == "__main__":
    viber.set_webhook("")
    time.sleep(1)
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, create_webhook, (viber, webhookURL,))
    t = threading.Thread(target=scheduler.run)
    t.start()

    app.run(host='0.0.0.0')
