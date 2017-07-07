# This Python file uses the following encoding: utf-8

import json
import requests
from database import DataBase
from time import gmtime, strftime
from driveAPI import BackuppedFile
from botApi import alertExc, alertBot


# when we start app.py

db = DataBase('parseRes.db')
#sync db

backup_db = BackuppedFile('parseRes.db')    # BACKUP_DB IS EXPORTED AS A CONST
backup_db.sync()


#------------------------------------------------------

try:
    db.format()
except:
    print("db already formatted")
print("!!!db created!!!")
del db
#------------------------------------------------------


# for phone numbers, not to use lambda
def evolve(a):
    if len(a) == 11:
        return a[1:]
    return a
    

# for optimizating work of all parsers
class Parse:
    name = ""
    #status_key = ""
    #results_file = ""
    db = None


    def __init__ (self, name):
        self.name = name
        #self.status_file = "./statuses/" + name + ".txt"
        #self.results_file = "./results/" + name + ".json"
        self.db = DataBase('parseRes.db')   # self db connection to enable multithreading
                                            # (MAYBE NO NEED FOR IT IN MULTIPROCESSING?)


    """def save_results(self, results):
        res = json.dumps(results)
        f = open(self.results_file, 'a', encoding='utf-8')
        f.write(res)
        f.close()"""


    # for statistics abouth the number of links processed
    def write_status(self, status):

        cmnd = "DELETE FROM Statuses WHERE name = '%s';" % self.name
        self.db.query(cmnd)

        cmnd = "INSERT INTO Statuses VALUES ('%s', '%s')" % (self.name, status)
        self.db.query(cmnd)
        

    # last updated on...
    def add_date(self):
        data = "last updated on: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        self.write_status(data)


    def get_results(self):
        cmnd = "SELECT * FROM Results WHERE fromwhere = '%s';" % self.name
        return str(self.db.fetch(cmnd))

    def get_status(self):
        cmnd = "SELECT status FROM Statuses WHERE name = '%s';" % self.name
        return self.db.fetch(cmnd)[0][0]

    # appending to db (like to a list)
    def append(self, data):       # working with db


        # get coordinates if we know adress
        def get_loc(adr):
            api_adr = adr.replace(' ', '+')
            url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % api_adr
            loc = requests.get(url).text
            loc = json.loads(loc)
            print("!!!GET_LOC USED!!!")
            loc = loc['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']["Point"]['pos']
            loc = list(loc.split(" "))
            loc = loc[1] + "," + loc[0]
            return loc


        # get adress if we know coordinates
        def get_adr(loc):
            url = "https://geocode-maps.yandex.ru/1.x/?geocode=%s&format=json&results=1" % loc
            adr = requests.get(url).text
            adr = json.loads(adr)
            print("!!!GET_ADR USED!!!")
            return adr['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['Address']['formatted']



    #  SET CHECK IF THE FLAT ALREADY EXISTS   !!!!!!!!!!!!!!!!!!!!!


    # getting loc and adr
        if ("adr" in data and "loc" not in data) or (data['loc'] == []) or (data['loc'] == ""):
            try:
                data["loc"] = get_loc(data["adr"])
            except:
                data['loc'] = "YANDEXLOCERR"
                print('YANDEXLOCERR')


        elif ("loc" in data and "adr" not in data) or (data['adr'] == ""):
            try:
                data["adr"] = get_adr(data["loc"])
            except:
                data['adr'] = 'YANDEXADRERR'
                print("YANDEXADRERR")
                
        # forming db command
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
'%s',
'%s',
'%s',
'%s',
"%s",
'%s',
'%s'
);
""" % (data['cost'], data['room_num'], data['area'], evolve(data['contacts']['phone'].replace("+7", "").replace(" ","").replace("-","").replace("(","").replace(")","")), data['date'], 'NULL', json.dumps(data['pics'], ensure_ascii=False), json.dumps(data['contacts'], ensure_ascii=False), data['descr'], data['adr'], json.dumps(data['metro'], ensure_ascii=False), data['url'], json.dumps(data['loc']), self.name)
        #print(cmnd)
        self.db.query(cmnd)
        print("\n\n-----ONE MORE WITH "+self.name+"-----\n\n")



    def __del__(self):
        del self.db



















    
