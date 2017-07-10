# This Python file uses the following encoding: utf-8

import threading
import json
#import driveAPI as dvp
from multiprocessing import Process
from parseAPI import parse_it
from bottle import *
from parser_class import Parse
from database import DataBase
from botApi import tgExcCatch, alertExc
from driveAPI import upload_db


#-------------------------before run------------------------

# info kept in txt files
# KEEP IT IN THE DB!!! (?) - for alerts -- yes, to be always synced!
PARSER_LIST = json.loads(open('parser_list.json', 'r').read())
#print(DataBase('parseRes.db').fetch("SELECT * FROM alerts;")[0][0][1:-1])

try:
    FORMAT_DIC = json.loads(DataBase('parseRes.db').fetch("SELECT * FROM alerts;")[0][0][1:-1])
except:
    FORMAT_DIC = {'version': 'unknown', 'added': '---', 'othertext': ''}

# creating all status rows
for p in PARSER_LIST:
    parsr = Parse(p)
    try:
        if parsr.get_status() == ' ':
            parsr.write_status('last updated on: never')
    except:
        parsr.write_status('last updated on: never')
        
    del parsr

#--------------------------server is here----------------------------


# parsers & their status
@get("/")
def main():
    return template("./html/main.html", version=FORMAT_DIC['version'], added=FORMAT_DIC['added'], othertext=FORMAT_DIC['othertext'])


# main with cms
@get("/adm/main")
def main():
    return template("./html/main-adm.html", version=FORMAT_DIC['version'], added=FORMAT_DIC['added'], othertext=FORMAT_DIC['othertext'])


# processing to change cms info
@get("/changemain")
def change():
    for param in request.query:
        if request.query[param] != "":
            FORMAT_DIC[param] = request.query[param]
    db = DataBase('parseRes.db')
    db.delete_table('alerts') # clear alerts
    db.query("""INSERT INTO alerts VALUES ('''%s''');""" % str(json.dumps(FORMAT_DIC, ensure_ascii=False)).encode('utf-8'))
    del db
    redirect("/adm/main")
    

# start parse (ALL parsers)
@get("/start_parse")
#@tgExcCatch
def st():              
    maxprice = request.query.maxprice
    db = DataBase('parseRes.db')
    db.delete_table('Results')
    del db
    for parser_name in PARSER_LIST:
        t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))    	
        t.daemon = True
        t.start()
    redirect("/")
    

# start parse (ONE parser)
@get("/special_parse")
def spp():
    #maxprice = int(request.query.maxprice)
    maxprice = 15000
    parser_name = request.query.parser_name
    t = threading.Thread(target = parse_it, args=(parser_name, maxprice,))
    t.daemon = True
    t.start()
    redirect('/')


# STOP PARSING (???)
@get("/stop_parsing")
#@tgExcCatch
def st():
    raise RuntimeError('now the server will restart!')


# get parsed results
@get("/res/<parser>")
def res(parser):
    return Parse(parser).get_results()


# get stats for a parser
@get("/parse_status/<parser>")
def return_status(parser):
    #resp.set_header("Cache-Control", 'no-store, no-cache, must-revalidate, max-age=0')
    return Parse(parser).get_status()


# all parsers list
@get("/plist")
def pl():
    return json.dumps(PARSER_LIST)


# download db
@get("/db")
def db():
    return static_file("parseRes.db", root='.', download=True)

'''
@get("/cn")
def cn():
    return static_file("cian.json", root='./results')'''


# parse social networks
@get("/start_social")
#@tgExcCatch
def st():
    n = int(request.query.num)
    t = threading.Thread(target=parse_it, args=('vk', n,))
    t.daemon = True
    t.start()
    redirect("/")


@get("/clear_results")
def clear():
    db = DataBase('parseRes.db')
    db.delete_table('Results')
    db.delete_table('Snimu')
    #db.format()
    del db
    redirect('/')

'''@post("/errorBot")
def err():
    print(request.json)
    return "OK"'''


'''@get("/zerodiv")
@tgExcCatch
def abc(a1, a2):
    a = 17/0
    #print(str(a))
    return(str(a))'''

@get("/sync_db")
def snc():
    #try:
    upload_db()
    redirect('/')
    #except:
     #   alertExc()
        
# run the server

run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
