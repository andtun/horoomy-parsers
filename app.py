# This Python file uses the following encoding: utf-8

import threading
import json
from parseAPI import parse_it
from bottle import *


PARSER_LIST = json.loads(open('parser_list.json', 'r').read())


@get("/")
def main():
    return static_file("main.html", root="./html")

@get("/start_parse")
def st():              
    maxprice = request.query.maxprice
    for parser_name in PARSER_LIST:
    	t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))
    	t.start()
    redirect("/")

@get("/res/<parser>")
def res(parser):
    filename = parser + "_res.json"
    return static_file(filename, root='.')

@get("/parse_status/<parser>")
def return_status(parser):
    filename = parser + "_st.txt"
    return static_file(filename, root='.')

@get("/plist")
def pl():
    return json.dumps(PARSER_LIST)


run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
