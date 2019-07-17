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
handler = logging.FileHandler('server viber bot.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


app = Flask(__name__)
api = flask_restful.Api(app)
'''@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"'''


TOKEN = '49d9448534e7d762-f3edf756728e1fda-f22cbe3cfebdf984'
webhookURL = 'https://server-test-ecoviewapp.fvds.ru/'

viber = Api(BotConfiguration(
    name='PeLabBot',
    avatar='',
    auth_token=TOKEN
))


@app.route('/', methods=["POST"])
def incoming():
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

        SAMPLE_BUTTON = """{
                    "Type": "keyboard",
                    "InputFieldState": "hidden",
                    "Buttons": [{
                        "Columns": 3,
                        "Rows": 1,
                        "ActionBody": "_bot_write_acii",
                        "Text": "Акции"
                    },{

                        "Columns": 3,
                        "Rows": 1,
                        "ActionBody": "_bot_search_articul",
                        "Text": "Поиск по артикулу"

                    }]
                }"""

        RETURNBUTTON = """{
                            "Type": "keyboard",
                            "InputFieldState": "hidden",
                            "Buttons": [{
                                "Columns": 6,
                                "Rows": 1,
                                "ActionBody": "_bot_home",
                                "Text": "Назад"
                            }]
                    }"""

        SAMPLE_RICH_MEDIA = """{
                              "BgColor": "#69C48A",
                              "Buttons": [
                                {
                                  "Columns": 6,
                                  "Rows": 1,
                                  "BgColor": "#454545",
                                  "BgMediaType": "gif",
                                  "BgMedia": "http://www.url.by/test.gif",
                                  "BgLoop": true,
                                  "ActionType": "open-url",
                                  "Silent": true,
                                  "ActionBody": "www.tut.by",
                                  "Image": "www.tut.by/img.jpg",
                                  "TextVAlign": "middle",
                                  "TextHAlign": "left",
                                  "Text": "<b>example</b> button",
                                  "TextOpacity": 10,
                                  "TextSize": "regular"
                                }
                              ]
                            }"""

        SAMPLE_ALT_TEXT = "upgrade now!"

        message = viber_request.message
        command = message.text

        if command == "Начать" or command == "начать":
            viber.send_messages(viber_request.sender.id, [
                KeyboardMessage(keyboard=json.loads(SAMPLE_BUTTON))
            ])

        if command == "_bot_search_articul":
            viber.send_messages(viber_request.sender.id, [
                TextMessage(text="Введите артикул для поиска"), KeyboardMessage(keyboard=json.loads(RETURNBUTTON))
            ])



        if command == "_bot_write_acii":
            viber.send_messages(viber_request.sender.id, [
                KeyboardMessage(keyboard=json.loads(RETURNBUTTON))
            ])

        if command == "_bot_home":
            viber.send_messages(viber_request.sender.id, [
                KeyboardMessage(keyboard=json.loads(SAMPLE_BUTTON))
            ])

        else:
            message = viber_request.message
            #message = "Select products.id_product, products.articul, prices.price, quantities.quantity, products.product FROM products LEFT JOIN prices on products.id_product = prices.id_product LEFT JOIN quantities on products.id_product = quantities.id_product WHERE articul LIKE "


            if len(str(message.text))>=4:
                #conn = psycopg2.connect(dbname='test-pe-lab', user='postgreadmin',password='5112274', host='78.24.216.107', port=5433)
                conn = psycopg2.connect(dbname='server-test-pe-lab', user='postgreadmin',password='5112274', host='78.24.216.107', port=5433)

                with conn.cursor() as cursor:
                    stmt = sql.SQL("Select products.id_product, products.articul, prices.price, quantities.quantity, products.product, prices.time_, products.link, products.image, prices.stock_price FROM products LEFT JOIN prices on products.id_product = prices.id_product and prices.date_ = current_date LEFT JOIN quantities on products.id_product = quantities.id_product and quantities.date_ = current_date WHERE articul ~* %s")
                   # viber.send_messages(viber_request.sender.id, [TextMessage(text=viber_request.message.text)])

                    cursor.execute(stmt, [message.text])
                    output = cursor.fetchall()
                    #viber.send_messages(viber_request.sender.id, [TextMessage(text=len(output[0]))])
                    data = {
                        #"receiver": viber_request.sender.id,
                        "type": "rich_media",
                        #"min_api_version": 6,
                        "rich_media": {
                            "Type": "rich_media",
                            "ButtonsGroupColumns": 6,
                            "ButtonsGroupRows": 7,
                            "BgColor": "#FFFFFF",
                            "Buttons":[

                            ]
                        }
                    }
                    for row in output:
                        #viber.send_messages(viber_request.sender.id, [TextMessage(text=row[0])])

                        data["rich_media"]["Buttons"].append(
                            {
                            "Columns": 6,
                            "Rows": 3,
                            "ActionType": "open-url",
                            "ActionBody": "https://ulabrus.ru/" + row[6],
                            "Image": "https://ulabrus.ru/" + row[7]
                            })
                        data["rich_media"]["Buttons"].append(
                            {
                                "Columns": 6,
                                "Rows": 2,
                                "Text": "<font color=#323232><b>" + row[1] + "," + row[4] + "</b></font>" + "<font color=#777777><br>Цена </font><font color=#6fc133>" + str(row[2]) + ", с учетом НДС 20%"+ "</font>" + "<font color=#777777><br>На складе </font><font color=#6fc133>" + str(row[3]) + "</font>"  + "<font color=#777777><br>Данные актуальны на </font><font color=#6fc133>" + str(row[5].strftime("%d.%m.%Y %H:%M")) + "</font>",
                                "ActionType": "open-url",
                                "ActionBody": "https://ulabrus.ru/" + row[6],
                                "TextSize": "medium",
                                "TextVAlign": "middle",
                                "TextHAlign": "left"
                            })
                        data["rich_media"]["Buttons"].append(
                            {
                                "Columns": 6,
                                "Rows": 1,
                                "ActionType": "reply",
                                "ActionBody": "https://ulabrus.ru/" + row[6],
                                "Text": "<font color=#8367db>ПОДРОБНЕЕ</font>",
                                "TextSize": "small",
                                "TextVAlign": "middle",
                                "TextHAlign": "middle"
                            }
                        )
                        if row[3] == None:
                            text_message = "Артикул: %s\nНаименование Полное:%s \nЦена: %s\nЦена по акции: %s\nКоличество на складе: 0\nДанные актуальны на: %s\nЗаказать: https://ulabrus.ru%s" % (row[1], row[4], str(locale.format('%.2f', row[2], grouping=True)).replace(",", ".")  + ", с учетом НДС 20%", str(locale.format('%.2f', row[8], grouping=True)).replace(",", ".")  + ", с учетом НДС 20%" if row[8] != None else "не проводится" , str(row[5].strftime("%d.%m.%Y %H:%M")), row[6])
                        else:
                            text_message = "Артикул: %s\nНаименование Полное:%s \nЦена: %s\nЦена по акции: %s\nКоличество на складе: %s\nДанные актуальны на: %s\nЗаказать: https://ulabrus.ru%s" % (row[1], row[4], str(locale.format('%.2f', row[2], grouping=True)).replace(",", ".") + ", с учетом НДС 20%", str(locale.format('%.2f', row[8], grouping=True)).replace(",", ".")  + ", с учетом НДС 20%" if row[8] != None else "не проводится" , str(row[3]), str(row[5].strftime("%d.%m.%Y %H:%M")), row[6])
                            # text_message = "hello"
                        #if row[6] != None:
                            #url_message = "https://ulabrus.ru/" + row[6]

                        #if row[7] != None:
                           # img_message = "https://ulabrus.ru/" + row[7]
                        viber.send_messages(viber_request.sender.id, [TextMessage(text=text_message), KeyboardMessage(keyboard=json.loads(RETURNBUTTON))])
                app_json = json.dumps(data)
                #api.add_resource(app_json, '')
                #viber.send_messages(viber_request.sender.id, [RichMediaMessage(rich_media=json.loads(app_json)), KeyboardMessage(keyboard=json.loads(RETURNBUTTON))])
            else:
                text_message = "Не могу найти товар.\nВведите, пожалуйста, не менее 4х символов!"
                viber.send_messages(viber_request.sender.id, [TextMessage(text=text_message), KeyboardMessage(keyboard=json.loads(RETURNBUTTON))])

            #RichMediaMessage(rich_media=json.loads(app_json))


               # logger.debug(message)





        # lets echo back
        '''viber.send_messages(viber_request.sender.id, [
            message
        ])
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.get_user.id, [
            TextMessage(text="thanks for subscribing!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}".format(viber_request))'''

    return Response(status=200)


def create_webhook(viber, webhookURL):
    print("hello")
    viber.set_webhook(webhookURL)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1>"


if __name__ == "__main__":
    viber.set_webhook("")
    time.sleep(1)
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, create_webhook, (viber, webhookURL,))
    t = threading.Thread(target=scheduler.run)
    t.start()

    app.run(host='0.0.0.0')
