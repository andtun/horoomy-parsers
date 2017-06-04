# This Python file uses the following encoding: utf-8

import threading
import parseAPI
from bottle import *

@get("/")
def main():
    return static_file("main.html", root='./html')

@get("/start_parse")
def st():
    t = threading.Thread(target = parseAPI.parse_cian)
    t.start()
    redirect("/")

@get("/res/<parser>")
def res(parser):
    filename = parser + "_res.json"
    return static_file(filename, root='.')

@get("/parse_status/<parser>")
def return_status(parser):
    filename = parser + ".txt"
    return static_file(filename, root='.')


run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
