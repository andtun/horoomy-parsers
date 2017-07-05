# This Python file uses the following encoding: utf-8

import threading
import json
from parseAPI import parse_it
from bottle import *
from parser_class import Parse
from database import DataBase
from botApi import tgExcCatch, alertExc


PARSER_LIST = json.loads(open('parser_list.json', 'r').read())
FORMAT_DIC = json.loads(open('alerts.json', 'r', encoding='utf-8').read())


# creating all status files
for p in PARSER_LIST:
    filename = "./statuses/"+p+".txt"
    try:
        f = open(filename, 'r')
        if "last updated on:" not in f.read():
            f.close()
            f = open(filename, 'w')
            f.write('last updated on: never')
            f.close()
    except:
        f = open(filename, 'w')
        f.write('last updated on: never')
        f.close()


@get("/")
def main():
    return template("./html/main.html", version=FORMAT_DIC['version'], added=FORMAT_DIC['added'], othertext=FORMAT_DIC['othertext'])


@get("/adm/main")
def main():
    return template("./html/main-adm.html", version=FORMAT_DIC['version'], added=FORMAT_DIC['added'], othertext=FORMAT_DIC['othertext'])


@get("/changemain")
def change():
    for param in request.query:
        if request.query[param] != "":
            FORMAT_DIC[param] = request.query[param]
    f = open('alerts.json', 'w', encoding='utf-8')
    f.write(json.dumps(FORMAT_DIC, ensure_ascii=False))
    f.close()
    redirect("/adm/main")

@get("/start_parse")
#@tgExcCatch
def st():              
    maxprice = request.query.maxprice
    db = DataBase('parseRes.db')
    db.query("DELETE FROM Results")
    del db
    for parser_name in PARSER_LIST:
        t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))    	
        t.daemon = True
        t.start()
    redirect("/")

@get("/special_parse/<parser_name>")
def spp(parser_name):
    maxprice = int(request.query.maxprice)
    t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))
    t.daemon = True
    t.start()

@get("/stop_parsing")
#@tgExcCatch
def st():
    raise RuntimeError('now the server will restart!')

@get("/res/<parser>")
def res(parser):
    p = DataBase('parseRes.db')
    res = p.fetch("SELECT * FROM Results WHERE fromwhere = '%s';" % parser)
    del p
    return str(res)

@get("/parse_status/<parser>")
def return_status(parser):
    filename = Parse(parser).status_file
    resp = static_file(filename, root='')
    resp.set_header("Cache-Control", 'no-store, no-cache, must-revalidate, max-age=0')
    return resp

@get("/plist")
def pl():
    return json.dumps(PARSER_LIST)

@get("/db")
def db():
    return static_file("parseRes.db", root='.', download=True)

@get("/cn")
def cn():
    return static_file("cian.json", root='./results')

@get("/start_social")
#@tgExcCatch
def st():
    n = int(request.query.num)
    t = threading.Thread(target=parse_it, args=('vk', n,))
    t.daemon = True
    t.start()
    redirect("/")

@post("/errorBot")
def err():
    print(request.json)
    return "OK"

'''@get("/zerodiv")
@tgExcCatch
def abc():
    a = 17/0
    #print(str(a))
    return(str(a))'''

run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
