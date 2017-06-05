# This Python file uses the following encoding: utf-8

import requests
import json
from bs4 import BeautifulSoup
from time import gmtime, strftime
import time

# set minmax price !!!!

class Parse:
    name = ""
    status_key = ""
    results_file = ""


    def __init__ (self, name):
        self.name = name
        self.status_file = name + "_st.txt"
        self.results_file = name + "_res.json"


    def save_results(self, results):
        res = results.encode('utf-8')
        f = open(self.results_file, 'w')
        f.write(res)
        f.close()


    def write_status(self, status):
        f = open(self.status_file, 'w')
        towrite = str(status) + " links processed"
        f.write(towrite)
        f.close()
        

    def add_date(self):
        data = "last updated on: " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        f = open(self.status_file, 'w')
        f.write(data)
        f.close()
                 
        
def cian():
    
    def getinf(url):
        all_images = []
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html5lib")
        infa = soup.find("div", {"class": "fotorama"})
        if infa == None:
            all_images = ["No Images"]
            return all_images
        else:
            images = infa.findAll("img")
            for i in images:
                x = i.get("src")
                all_images.append(x)
            return all_images


    url = "https://map.cian.ru/ajax/map/roundabout/?deal_type=rent&engine_version=2&offer_type=flat&region=1&room1=1&room2=1&room3=1&maxprice=40000"
    p = Parse("cian")
    link_template = 'https://cian.ru/rent/flat/'

    #f = open("pres.txt", 'w')
    #f.write("Parsing right now, check your logs")
    #f.close()

    # { 'room_num': "", 'metro': [список с ближайшими станциями метро], 'pics': [список с фото квартиры],
    #  cost: "цена квартиры", floor: "этаж", phone: "телефон хозяина", furn: True/False, loc: [координаты],
    #  long: True/False, agent: True/False}

    all_infa = []
    html = requests.get(url).text
    json_text = json.loads(html)
    infa = json_text["data"]["points"]
    
    count = 0
    for i in infa:
        main = infa[i]
        offers = main["offers"]
        
        for j in offers:
            room_num = j['property_type']
            price = j['price_rur']
            floor = j["link_text"][3]
            floor = floor[floor.find(" ") + 1:]
            flat_id = j["id"]
            print("I'm still processing")
            
        url = link_template + flat_id
        all_pics = getinf(url)

        print(url)
        count += 1
        p.write_status(count)
        
        x = {'room_num': room_num, 'metro': [], 'pics': all_pics,
         "cost": price, "floor": floor, "phone": "телефон", "furn": None, "loc": i,
         "long": None, "agent": None, "link": url}
        all_infa.append(x)
        
    p.save_results(all_infa)
    print("ALL INFA WRITTEN")
    p.add_date()

