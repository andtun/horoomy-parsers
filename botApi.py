# This Python file uses the following encoding: utf-8

import requests


ERROR_CHAT_ID = '273633310'


class Bot:
    full_link = ""

    def __init__(self, chat_id):
        self.full_link = "https://api.telegram.org/bot332143024:AAFXvkc397uXcvN3HgbiKQ0GTaNXKf-H-zs/%s&chat_id="+chat_id

    def sendMessage(self, text):
        link_text = "sendMessage?text="+text
        requests.get(self.full_link % link_text)


def tgErrCatch(func):
    def wrapper():
        try:
            func()
        except Exception as e:
           Bot(ERROR_CHAT_ID).sendMessage(str(e))

        return wrapper
