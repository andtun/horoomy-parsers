# This Python file uses the following encoding: utf-8

import requests
import json
from bs4 import BeautifulSoup
import time


def parse_cian():
    
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


    def write(d):
        

    def final_write(d):
        d = str(d)
        f = open("cian_res.json", 'w')
        f.write(d)
        f.close()
        

    url = "https://map.cian.ru/ajax/map/roundabout/?currency=2&deal_type=rent&engine_version=2&maxprice=50000&offer_type=flat&region=1&room1=1&type=4"

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
        print(url)
        towrite = str(infa.index(i)) + "links processed"
        write(towrite)
        all_pics = getinf(url)
        x = {'room_num': room_num, 'metro': [], 'pics': all_pics,
         "cost": price, "floor": floor, "phone": "телефон", "furn": None, "loc": i,
         "long": None, "agent": None, "link": url}
        all_infa.append(x)
    final_write(all_infa)
    print("ALL INFA WRITTEN")

