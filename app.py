# This Python file uses the following encoding: utf-8

import threading
import json
from parseAPI import parse_it
from bottle import *
from parser_class import Parse
from database import DataBase


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
    p = DataBase('parseRes.db')
    res = p.fetch("SELECT json FROM Results WHERE fromwhere = '%s';" % parser)
    del p
    return str(res).encode('unicode_escape')

@get("/parse_status/<parser>")
def return_status(parser):
    filename = Parse(parser).status_file
    return static_file(filename, root='')

@get("/plist")
def pl():
    return json.dumps(PARSER_LIST)

@get("/db")
def db():
    return static_file("parseRes.db", root='.', download=True)

@get("/cn")
def cn():
    return static_file("cian.json", root='./results')


run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
