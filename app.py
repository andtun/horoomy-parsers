# This Python file uses the following encoding: utf-8

import threading
import parseAPI
from bottle import *

@get("/start_parse")
def st():
    t = threading.Thread(target = parseAPI.parse_cian)
    t.start()
    redirect("/res")

@get("/res")
def res():
    return static_file("pres.txt", root='.')


run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
