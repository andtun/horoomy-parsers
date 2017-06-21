# This Python file uses the following encoding: utf-8

import threading
import json
from parseAPI import parse_it
from bottle import *
from parser_class import Parse
from database import DataBase


PARSER_LIST = json.loads(open('parser_list.json', 'r').read())

# creating all status files
for p in PARSER_LIST:
    filename = "./statuses/"+p+".txt"
    f = open(filename, 'w')
    f.write('last updated on: never')
    f.close()


@get("/")
def main():
    return static_file("main.html", root="./html")

@get("/start_parse")
def st():              
    maxprice = request.query.maxprice
    db = DataBase('parseRes.db')
    db.query("DELETE FROM Results")
    del db
    for parser_name in PARSER_LIST:
    	t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))    	
    	t.start()
    redirect("/")

@get("/special_parse/<parser_name>")
def spp(parser_name):
    maxprice = int(request.query.maxprice)
    t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))
    t.start()

@get("/res/<parser>")
def res(parser):
    p = DataBase('parseRes.db')
    res = p.fetch("SELECT * FROM Results WHERE fromwhere = '%s';" % parser)
    del p
    return str(res)

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
