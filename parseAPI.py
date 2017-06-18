# This Python file uses the following encoding: utf-8

import requests
import json
import time
from bs4 import BeautifulSoup
from time import gmtime, strftime
from parser_class import Parse

# set minmax price !!!!


        
def cian(maxprice):
    
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


    url = "https://map.cian.ru/ajax/map/roundabout/?deal_type=rent&engine_version=2&offer_type=flat&region=1&room1=1&room2=1&room3=1&maxprice=" + str(maxprice)
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
    p.add_date() #я не умею эту фигню писать


# ===========================================================================================================


def get_html(url):
    r = requests.get(url)
    print(str(r), end=' ')
    return r.text

def get_page_data(html):

    soup = BeautifulSoup(html, 'lxml')

    media = soup.find('section', class_='clear-fix').find('div', class_ = 'object-block').find('div', class_="object-info-block").find('div', class_='object-media')
    info = soup.find('section', class_='clear-fix').find('div', class_ = 'object-block').find('div', class_="object-info-block").find('div', class_='object-info')


    #price
    #try:
    cost = soup.find('section', class_='clear-fix').find('div', class_ = 'object-block').find('div', class_="object-info-block").find('div', class_='object-price').text.split('/')[0][:-2]
    cost = cost.split()
    cost = int(''.join(cost))
    #except:
    #cost = '-'

    #metro
    try:
        metro = []
        metro.append(info.find('div', class_='object-info-link_l1').find('a').text)
    except:
        metro = []

    #Address
    # try:
    adr = ''
    elms = info.find('div', class_='object-info-link_l2').find_all('a')
    for elm in elms:
        adr += elm.text + ' '
# except:
#   adr = '-'       

    #Created date
    date = media.find('div', class_='obj-info-dop').text.split()[1][:-1]
        #date = '-'


    temp = info.find('div', class_='object-params').find('div',class_='params-block').find_all('div', class_='params-item')
    for i in range(len(temp)):
        t = temp[i].find('div', class_='float-left').text
        if 'Количество комнат' in t:
            room_num_i = i
        elif 'Общая площадь' in t:
            area_i = i  


    #Rooms
    room_num = info.find('div', class_='object-params').find('div',class_='params-block').find_all('div', class_='params-item')[room_num_i].find('div',class_='float-right').text
    if room_num == 'комната':
        room_num = 1
    else:
        room_num = int(room_num)    



    #Area
    area = int(info.find('div', class_='object-params').find('div',class_='params-block').find_all('div', class_='params-item')[area_i].find('div',class_='float-right').text.split()[0])

    
    #Description

    descr = info.find('div', class_='object-description').find('div', class_='object-description-text').text

    pics = []
    template = 'http://www.realestate.ru'
    elms = media.find('div', class_='object-photo').find('div', class_='other-photo-container').find_all('img', class_='other-photo')
    if elms:
        for elm in elms:
            pics.append(template + elm.get('src'))



    #Contacts

    contacts = {'vk': "", 'fb': "", 'email': "", 'phone': ""}
    add = int(media.find('div', class_='obj-active-panel').find('div', class_='toogle-button').get('blst'))
    if add == 0:
        add = int(media.find('div', class_='obj-active-panel').find('div', class_='toogle-button').get('lst1'))
    add = str(add//17)[1:]  
    phone = media.find('div',class_='object-connect').find('div',class_='object-builder-phone_block').find('div', class_='object-builder-phone').text[:-3] + add
    print(phone)
    contacts['phone'] = phone


    #loc

    headers = {
        'Referer': 'http://www.realestate.ru/flatrent/4320916/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    response = requests.get('http://www.realestate.ru/scripts/common/ymaps.js', headers=headers).text
    start = response.find("center:") + 9
    ch = ''
    i = 0
    while ch != ']':
        ch = response[start+i]
        i += 1
    end = start + i -1
    loc = response[start:end].split(',')

    return date, cost, descr, pics, room_num, area, adr, metro, contacts, loc

    #Location // Можно вытащить из названия объявления



def get_total_pages(url):
    soup = BeautifulSoup(get_html(url), 'lxml')
    total_pages = soup.find('section', class_='clear-fix').find_all('div', class_='contentblock')[1].find('div', class_='main-content').find('div', class_='list-panel').find('div', class_='more-info').find_all('a')[-1].get('href').split('pg')[1][:-1]
    return int(total_pages)




def realestate(maxprice):
    p = Parse('realEstate')
    currentPage = 1
    template = 'http://www.realestate.ru'
    page_url_template = 'http://www.realestate.ru/flatrent/s/rcs10.1.2.3-prt{0}/pg'.format(maxprice//1000)#'http://www.realestate.ru/flatrent/pg'
    page_url = page_url_template  + str(currentPage) + '/'
    total_pages = get_total_pages(page_url)+1
    out = []

    for currentPage in range(int(str(total_pages)[1:])):
        # if currentPage == 2:
        #   break   
        page_url = page_url_template  + str(currentPage) + '/'
        soup = BeautifulSoup(get_html(page_url), 'lxml')
        ads = soup.find('section', class_='clear-fix').find_all('div', class_='contentblock')[1].find('div', class_='main-content').find('div', class_='list-panel').find_all('div', class_='obj')
        for ad in ads:
            url = template + ad.find('div', class_='obj-item').find('a').get('href')
            #lat = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lat') # Получаем широту и долготу
            #lng = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lng') # скрытые в названии объявления
            html = get_html(url)
            print(url)
            date, cost, descr, pics, room_num, area, adr, metro, contacts, loc = get_page_data(html)
            data = {'date': date, 'cost': cost, 'descr': descr, 'pics':pics, 'room_num': room_num, 'area':area, 'adr':adr, 'metro': metro, 'url': url, 'loc': loc, 'contacts':contacts}
            p.append(data)
            p.write_status(currentPage)
            print('{0}% Current page: {1}'.format(int(currentPage/total_pages*100),currentPage))
            #time.sleep(3)

      p.add_date()     




#===========================================OPTIMIZATION============================================#

def parse_it(name, maxprice):
    if name == 'cian':
        cian(maxprice)
    elif name == 'realEstate':
        realestate(maxprice)
