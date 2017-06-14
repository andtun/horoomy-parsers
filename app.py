# This Python file uses the following encoding: utf-8

import threading
from parseAPI import parse_it
from bottle import *


PARSER_LIST = ['cian', 'realEstate']


def main_page():
    div = ""
    for p in PARSER_LIST:
        div += """<div><span style="margin-right: 20%; margin-left: 3%;">{0}:</span><span id="{0}" style="margin-right: 17%;">xtnf</span><button onclick="window.location = '/res/{0}';">Просмотреть результаты</a></div>""".format(p)
    return template("./html/main.html", plist = str(PARSER_LIST), parserdivs = div)


@get("/")
def main():
    return main_page()

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


run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
