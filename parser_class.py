# This Python file uses the following encoding: utf-8

import json
import requests
from database import DataBase

# when we start app.py
db = DataBase('parseRes.db')
try:
    db.format()
except:
    print("db already formatted")
print("!!!db created!!!")
del db


class Parse:
    name = ""
    status_key = ""
    results_file = ""
    db = None


    def __init__ (self, name):
        self.name = name
        self.status_file = "./statuses/" + name + ".txt"
        self.results_file = "./results/" + name + ".json"
        self.db = DataBase('parseRes.db')


    def save_results(self, results):
        res = json.dumps(results)
        f = open(self.results_file, 'w', encoding='utf-8')
        f.write(res)
        f.close()


    def write_status(self, status):
        f = open(self.status_file, 'w', encoding='utf-8')
        towrite = str(status) + " links processed"
        f.write(towrite)
        f.close()
        

    def add_date(self):
        data = "last updated on: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        f = open(self.status_file, 'w', encoding='utf-8')
        f.write(data)
        f.close()


    def append(self, data):       # working with db

        def get_loc(adr):
            api_adr = adr.replace(' ', '+')
            url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % api_adr
            loc = requests.get(url).text
            loc = json.loads(loc)
            return loc['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["Point"]['pos']

        def get_adr(loc):
            url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % loc
            adr = requests.get(url).text
            adr = json.loads(adr)
            return adr['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']

        if "adr" in data and "loc" not in data:
            data["loc"] = get_loc(data["adr"])

        elif "loc" in data and "adr" not in data:
            data["adr"] = get_adr(data["loc"])
        
        cmnd = """
INSERT INTO Results VALUES (
NULL,
%s,
%s,
%s,
'%s',
'%s',
'%s',
'%s',
'%s'
);
""" % (data['cost'], data['room_num'], data['area'], data['contacts']['phone'], data['date'], 'NULL', json.dumps(data), self.name)

        self.db.query(cmnd)





















    
