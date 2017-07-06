# This Python file uses the following encoding: utf-8

import re
import requests
import json
import time
import datetime
import threading
from botApi import alertExc, tgExcCatch, alertBot
from bs4 import BeautifulSoup
from time import gmtime, strftime
from parser_class import Parse
from datetime import datetime, timedelta
from driveAPI import BackuppedFile

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
         "cost": price, "floor": floor, "contacts": {"phone": "телефон"}, "furn": None, "loc": i.replace(' ', ','),
         "long": None, "agent": None, "link": url}
        p.save_results(x)
        
    print("ALL INFA WRITTEN")
    p.add_date()


# ===========================================================================================================

def realestate(maxprice):
    
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
        # adr = ''
        # elms = info.find('div', class_='object-info-link_l2')#.find_all('a')
        # # for elm in elms:
        # #     print(elm)
        # #     adr += elm.text + ' '
        # print(elms)       
    # except:
    #   adr = '-'       

        #Created date
        date = media.find('div', class_='obj-info-dop').text.split()[1][:-1]
        date = date.split('.')
        date[2] = '20' + str(date[2])
        date = '.'.join(date)
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
        #print(phone)
        contacts['phone'] = phone


        #loc
        # loc = []
        # if not adr:
        #   headers = {
        #       'Referer': 'http://www.realestate.ru/flatrent/4320916/',
        #       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        #   }

        #   response = requests.get('http://www.realestate.ru/scripts/common/ymaps.js', headers=headers).text
        #   start = response.find("center:") + 9
        #   ch = ''
        #   i = 0
        #   while ch != ']':
        #       ch = response[start+i]
        #       i += 1
        #   end = start + i -1
        #   loc = response[start:end].split(',')


        #print(date, cost, room_num, area, contacts, sep = '\n')
        return date, cost, descr, pics, room_num, area, metro, contacts

        #Location // Можно вытащить из названия объявления



    def get_total_pages(url):
        soup = BeautifulSoup(get_html(url), 'lxml')
        total_pages = soup.find('section', class_='clear-fix').find_all('div', class_='contentblock')[1].find('div', class_='main-content').find('div', class_='list-panel').find('div', class_='more-info').find_all('a')[-1].get('href').split('pg')[1][:-1]
        return int(total_pages)




    def realest(maxprice):
        maxprice = int(maxprice)
        p = Parse('realEstate')
        currentPage = 1
        template = 'http://www.realestate.ru'
        #http://www.realestate.ru/flatrent/s/rcs10.1.2.3-rgs1.2.3.4.5.6.7.8.9.10-prt30/
        page_url_template = 'http://www.realestate.ru/flatrent/s/rcs10.1.2.3--rgs1.2.3.4.5.6.7.8.9.10-prt{0}/pg'.format(maxprice//1000)#'http://www.realestate.ru/flatrent/pg'
        page_url = page_url_template  + str(currentPage) + '/'
        total_pages = get_total_pages(page_url)+1
        out = []
        for currentPage in range(total_pages):
            # if currentPage == 2:
            #   break   
            page_url = page_url_template  + str(currentPage) + '/'
            soup = BeautifulSoup(get_html(page_url), 'lxml')
            ads = soup.find('section', class_='clear-fix').find_all('div', class_='contentblock')[1].find('div', class_='main-content').find('div', class_='list-panel').find_all('div', class_='obj')

            for ad in ads:
                url = template + ad.find('div', class_='obj-item').find('a').get('href')
                #lat = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lat') # Получаем широту и долготу
                #lng = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lng') # скрытые в названии объявления
                adr = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').text
                #print(adr)
                html = get_html(url)
                #print(url)
                date, cost, descr, pics, room_num, area, metro, contacts= get_page_data(html)
                data = {'date': date, 'cost': cost, 'descr': descr, 'pics':pics, 'room_num': room_num, 'area':area, 'adr':adr, 'metro': metro, 'url': url, 'contacts':contacts}
                p.append(data)
                
                # with open('out.txt', 'w', encoding='utf-8') as out_file:
                #   out_file.write(str(out))
                p.write_status(currentPage)
                #time.sleep(3)
        p.add_date()

    # run
    realest(maxprice)

#===================================================================================================#



def kvartirant(maxprice):


    def get_html(url):
        r = requests.get(url)
        print(r, end=' ')
        return r.text


    def get_page_data(html, url):

        print(url)

        #max_price = 30000
        
        soup = BeautifulSoup(html, 'lxml')
        base = soup.find('div', class_='boxed-container').find_all('div', class_='bg_lightgray')[0].find('div', class_='container').find('div', class_='col-md-8 col-obj').find('div', class_='row')

        #f
        area = ''
        metro = ''
        adr = ''

        temp = base.find('div', class_='col-xs-12 obj-info').find_all('span')
        for i in range(len(temp)):
            if 'Площадь' in temp[i].text:
                try:
                    area = float(temp[i].text.split()[1])
                except:
                    area = '-'  
            elif 'Метро' in temp[i].text:
                metro = temp[i].text.split('\u2022')
                metro[0] = ' '.join(metro[0].split()[1:])   
            elif 'Адрес' in temp[i].text:
                adr = temp[i].text.split()[1:]  
                adr = ' '.join(adr)

        #print(area, metro, adr)        

        #Определяем, посуточная аренда или нет
        try:
            isDaily = base.find('div', class_='col-xs-12 obj-info').find_all('span', class_='red')[1].text
            if isDaily == 'ПОСУТОЧНАЯ АРЕНДА':
                return False
        except:
            pass

        #prepay 
        # prepay = base.find('div', class_='col-xs-12 obj-info').find_all('span')[1].text
        # if 'Предоплата' in prepay or 'Новостройка' in prepay:
        #   offset = 1
        #   temp = base.find('div', class_='col-xs-12 obj-info').find_all('span')[2].text
        #   if 'Предоплата' in temp or 'Новостройка' in temp:
        #       offset = 2
        # else:
        #   offset = 0

        #Metro
        # if metro_i:
        #   metro = base.find('div', class_='col-xs-12 obj-info').find_all('span')[metro_i].text.split('\u2022')#.replace('\u2022','').split()[1:]
        #   metro[0] = ' '.join(metro[0].split()[1:])
        # else:
        #   metro = []  


        #Room number
        room_num = int(base.find('div', class_='col-xs-12 obj-info').find('h3').text.split()[2].split('-')[0])  
        # if room_num > 3:
        #   return False


        #Cost
        cost = base.find('div', class_='col-xs-12 obj-info').find('h3').find('span', class_='text-nowrap red').text
        cost = cost.split()[1:]
        cost = int(''.join(cost))
        # if cost > max_price:
        #   return False

        #Date
        
        date = base.find('div', class_='col-xs-12 col-sm-4 text-center padding_t10 obj-data').text.split()[0].split(':')[1]
        if(date=='Сегодня'):
            date = str(datetime.today()).split()[0].split('-')
            date = '.'.join(list(reversed(date)))
        else:
            date = date.replace('/','.')


        #Contacts
        contacts = {'vk': "", 'fb': "", 'email': "", 'phone': ""}
        phone = base.find('div', class_='col-xs-12 col-sm-8 padding_t10 obj-contact').find('span', class_='red').find('b').text.split("write('")[-1][:-2] #Вот такой-вот костыль
        contacts["phone"] = phone


        #Area
        # if area_i:
        #   area = base.find('div', class_='col-xs-12 obj-info').find_all('span')[area_i].text.split()[1]
        #   if area != '-':
        #       area = float(area)
        #       print(area)
        #   else:
        #       area = '-'  
        # else:
        #   area = '-'          


        #Adr
        # if adr_i:
        #   adr = base.find('div', class_='col-xs-12 obj-info').find_all('span')[adr_i].text.split()[1:]
        #   adr = ' '.join(adr)
        # else:
        #   adr = '-'       
        #print(adr)


        #Descr
        descr = base.find('div', class_='col-xs-12 obj-info').find('p').text        


        #Pics
        pics = []
        temp = base.find('div', class_='text-center col-xs-12 obj-info').find('div', class_='bxContainer').find('ul').find_all('li')
        for li in temp:
            pics.append(li.find('a').get('href'))

        #loc 
        loc = []
        if not adr or adr == '-':
            temp  = str(soup.find_all('script', type='text/javascript')[-1])
            sr = temp.find("ymaps.geocode('")
            start = sr+15
            i = 0
            ch = ''
            while ch != "'":
                ch = temp[start+i]
                i += 1
            loc = temp[start:start+i-1].split()


        data = {"cost": cost, "date": date, "contacts": contacts, "pics": pics, "descr": descr, "adr": adr, "loc": loc, "metro": metro, "area": area, "room_num": room_num, "url": url}
        return data


    def get_total_pages(html):
        soup = BeautifulSoup(html, 'lxml')

        # try:
        #   total_pages = soup.find('div', class_ = 'boxed-container').find('div',class_='base-pagination').find('div', class_='container').find('ul').find_all('li')[-1].find('a').text
        # except Exception as err:
        #   print(err)
        #   exit()  
        total_pages = soup.find('div', class_='boxed-container').find('div', class_='base-pagination').find('ul', class_='pagination').find('li', class_='last').find('a').get('data-page')

        return int(total_pages)+1   


    def get_objects_group(html):
        soup = BeautifulSoup(html, 'lxml')
        groups = soup.find('div', class_ = 'boxed-container').find_all('div', class_='bg_lightgray')[0].find('div', class_='container').find_all('div', class_='col-md-8 col-obj')
        return groups       


    def kvartir (maxprice):
        # maxprice = 30000
        base_url = 'http://www.kvartirant.ru/bez_posrednikov/Moskva/sniat-kvartiru/'
        params = '&cost_limit={0}&komnat[]=1&komnat[]=2&komnat[]=3'.format(maxprice)
        template = 'http://www.kvartirant.ru'
        html = get_html(base_url)
        counter = 0
        # out = []
        total_pages = get_total_pages(html)
        for page in range(total_pages)[1:]:
            p = Parse('kvartirant')
            url = base_url + '?page=' + str(page) + params
            html = get_html(url)
            groups = get_objects_group(html)
            for group in groups:
                ads = group.find('div', class_='row').find_all('div', class_='obj-contact')
                for ad in ads:
                    try:
                        url = ad.find('span', class_='red').find('b').find('a').get('href')
                        temp_html = get_html(template + url)
                        print('Page ' + str(page), end = ' - ')
                        page_data = get_page_data(temp_html, template+url)
                        counter += 1
                        p.write_status(counter)
                        if page_data:
                            p.append(page_data)
                            print('Success')
                        else:
                            print('Daily')# | room_num more than 3 rooms | cost more than maxprice')
                    except Exception as e:
                        alertExc()
            del p
            # with open('text.txt', 'w', encoding='utf-8') as out_file:
            #   out_file.write(str(out))
            # break 

        print('Done!')
        p = Parse('kvartirant')
        p.add_date()
        #return out
        del p


        # run
    kvartir(int(maxprice))


#---------------------------KVARTIRANT-FOR-ROOMS-----------------------------#


def kvartirant_room():
    
    def get_html(url):
        r = requests.get(url)
        print(r, end=' ')
        return r.text


    def get_page_data(html, url):

        print(url)

        #max_price = 30000
        
        soup = BeautifulSoup(html, 'lxml')
        base = soup.find('div', class_='boxed-container').find_all('div', class_='bg_lightgray')[0].find('div', class_='container').find('div', class_='col-md-8 col-obj').find('div', class_='row')

        #f
        area = ''
        metro = ''
        adr = ''

        temp = base.find('div', class_='col-xs-12 obj-info').find_all('span')
        for i in range(len(temp)):
            if 'Площадь' in temp[i].text:
                try:
                    area = float(temp[i].text.split()[1])
                except:
                    area = '-'  
            elif 'Метро' in temp[i].text:
                metro = temp[i].text.split('\u2022')
                metro[0] = ' '.join(metro[0].split()[1:])   
            elif 'Адрес' in temp[i].text:
                adr = temp[i].text.split()[1:]  
                adr = ' '.join(adr)

        #print(area, metro, adr)        

        #Определяем, посуточная аренда или нет
        try:
            isDaily = base.find('div', class_='col-xs-12 obj-info').find_all('span', class_='red')[1].text
            if isDaily == 'ПОСУТОЧНАЯ АРЕНДА':
                return False
        except:
            pass

        #prepay 
        # prepay = base.find('div', class_='col-xs-12 obj-info').find_all('span')[1].text
        # if 'Предоплата' in prepay or 'Новостройка' in prepay:
        #   offset = 1
        #   temp = base.find('div', class_='col-xs-12 obj-info').find_all('span')[2].text
        #   if 'Предоплата' in temp or 'Новостройка' in temp:
        #       offset = 2
        # else:
        #   offset = 0

        #Metro
        # if metro_i:
        #   metro = base.find('div', class_='col-xs-12 obj-info').find_all('span')[metro_i].text.split('\u2022')#.replace('\u2022','').split()[1:]
        #   metro[0] = ' '.join(metro[0].split()[1:])
        # else:
        #   metro = []  


        #Room number
        room_num = 0
        # if room_num > 3:
        #   return False


        #Cost
        cost = base.find('div', class_='col-xs-12 obj-info').find('h3').find('span', class_='text-nowrap red').text
        cost = cost.split()[1:]
        cost = int(''.join(cost))
        # if cost > max_price:
        #   return False

        #Date
        date = base.find('div', class_='col-xs-12 col-sm-4 text-center padding_t10 obj-data').text.split()[0].split(':')[1]
        if(date=='Сегодня'):
            date = str(datetime.today()).split()[0].split('-')
            date = '.'.join(list(reversed(date)))
        else:
            date = date.replace('/','.')


        #Contacts
        contacts = {'vk': "", 'fb': "", 'email': "", 'phone': ""}
        phone = base.find('div', class_='col-xs-12 col-sm-8 padding_t10 obj-contact').find('span', class_='red').find('b').text.split("write('")[-1][:-2] #Вот такой-вот костыль
        contacts["phone"] = phone


        #Area
        # if area_i:
        #   area = base.find('div', class_='col-xs-12 obj-info').find_all('span')[area_i].text.split()[1]
        #   if area != '-':
        #       area = float(area)
        #       print(area)
        #   else:
        #       area = '-'  
        # else:
        #   area = '-'          


        #Adr
        # if adr_i:
        #   adr = base.find('div', class_='col-xs-12 obj-info').find_all('span')[adr_i].text.split()[1:]
        #   adr = ' '.join(adr)
        # else:
        #   adr = '-'       
        #print(adr)


        #Descr
        descr = base.find('div', class_='col-xs-12 obj-info').find('p').text        


        #Pics
        pics = []
        temp = base.find('div', class_='text-center col-xs-12 obj-info').find('div', class_='bxContainer').find('ul').find_all('li')
        for li in temp:
            pics.append(li.find('a').get('href'))

        #loc 
        loc = []
        if not adr or adr == '-':
            temp  = str(soup.find_all('script', type='text/javascript')[-1])
            sr = temp.find("ymaps.geocode('")
            start = sr+15
            i = 0
            ch = ''
            while ch != "'":
                ch = temp[start+i]
                i += 1
            loc = temp[start:start+i-1].split()


        from math import trunc
        try:
            area = trunc(float(area))
        except:
            area = 0

        data = {"cost": cost, "date": date, "contacts": contacts, "pics": pics, "descr": descr, "adr": adr, "loc": loc, "metro": metro, "area": area, "room_num": room_num, "url": url}
        return data


    def get_total_pages(html):
        soup = BeautifulSoup(html, 'lxml')

        # try:
        #   total_pages = soup.find('div', class_ = 'boxed-container').find('div',class_='base-pagination').find('div', class_='container').find('ul').find_all('li')[-1].find('a').text
        # except Exception as err:
        #   print(err)
        #   exit()  
        total_pages = soup.find('div', class_='boxed-container').find('div', class_='base-pagination').find('ul', class_='pagination').find('li', class_='last').find('a').get('data-page')

        return int(total_pages)+1   


    def get_objects_group(html):
        soup = BeautifulSoup(html, 'lxml')
        groups = soup.find('div', class_ = 'boxed-container').find_all('div', class_='bg_lightgray')[0].find('div', class_='container').find_all('div', class_='col-md-8 col-obj')
        return groups       


    def realestate ():
        counter = 0
        maxprice = 30000
        base_url = 'http://www.kvartirant.ru/Moskva/sniat-komnatu/'
        params = '&cost_limit={0}'.format(maxprice)
        template = 'http://www.kvartirant.ru'
        html = get_html(base_url)
        #out = []
        p = Parse('kvartirant')
        total_pages = get_total_pages(html)
        for page in range(total_pages)[1:]:
            url = base_url + '?page=' + str(page) + params
            html = get_html(url)
            groups = get_objects_group(html)
            for group in groups:
                ads = group.find('div', class_='row').find_all('div', class_='obj-contact')
                for ad in ads:
                    counter += 1
                    url = ad.find('span', class_='red').find('b').find('a').get('href')
                    temp_html = get_html(template + url)
                    print('Page ' + str(page), end = ' - ')
                    page_data = get_page_data(temp_html, template+url)
                    if page_data:
                        p.append(page_data)
                        print('Success')
                    else:
                        print('Daily')# | room_num more than 3 rooms | cost more than maxprice')
                    p.write_status(counter)

        p.add_date()
        del p
        print('Done!')
        #return out

    realestate()


#===================================================================================================#



def parse_rentookiru(maxprice):

    # offers = []
    # Iterate page indexes
    page_index = 1
    while True:
        # Get page
        offers_page_html = requests.get("http://rentooki.ru/moscow/?page={0}".format(page_index)).text
        offers_page = BeautifulSoup(offers_page_html, "lxml")

        # Extract offer links
        links = offers_page.find_all("a", class_="pull-left relative", href=True)
        links = [x["href"] for x in links]

        # Exit on end
        if "Следующая" not in offers_page_html:
            print("\nNo sleduyushaya!!!\n")
            break

        for link in links:
            p = Parse('rentooki')
            try:

                # Get offer page
                offer_page = BeautifulSoup(requests.get("http://rentooki.ru{0}".format(link)).text, "lxml")

                # Extract title info
                title = offer_page.find("h2").contents[0]
                title = " ".join(title.split())

                # Split title to fields
                try:
                    offer_type_field, area_field, floor_field = title.split(",")
                except:
                    continue

                # Skip rooms
                # if offer_type_field.startswith("Сдам комнату"):
                #    continue

                # Placement date
                datetime_field = offer_page.find("small").contents[0].replace("Размещено", "").strip()
                try:
                    dt = datetime.strptime(datetime_field, "%d %b %H:%M")
                    dt = dt.replace(year=datetime.now().year)
                    print(dt)
                except:
                    if "cегодня" in datetime_field:
                        datetime_field = re.match(r".+ (\d+:\d+)", datetime_field).group(1)
                        dt = datetime.strptime(datetime_field, "%H:%M")
                        dt = datetime.now().replace(hour=dt.hour, minute=dt.minute)
                    elif "вчера" in datetime_field:
                        datetime_field = re.match(r".+ (\d+:\d+)", datetime_field).group(1)
                        dt = datetime.strptime(datetime_field, "%H:%M")
                        dt = datetime.now().replace(hour=dt.hour, minute=dt.minute)
                        dt = dt - timedelta(days=1)
                    else:
                        continue


                # Extract rooms number
                #room_number = int(re.match(r".+ (\d)-к ", offer_type_field).group(1))
                room_number = list(str(offer_type_field).split(" "))[2]
                if room_number != 'комната':
                    room_number = int(room_number[0])
                else:
                    room_number = 0
                # Extract area
                area = int(re.match(r"(\d+)", area_field.strip()).group(1))
                # Extract floor
                floor = int(re.match(r"(\d+)/", floor_field.strip()).group(1))

                # Cost and phone
                list_group = offer_page.find_all("li", class_="list-group-item")
                cost = int(list_group[0].next_element.next_element.contents[0].replace(" ", ""))
                if int(cost) > int(maxprice):
                    print("!!!MORE THAN MAXPRICE!!!")
                    continue
                #adr = list_group[1].contents[0].replace("\n", "").strip()
                descr = list_group[2].next_element.contents[0]
                contact_phone = list_group[4].next_element
                a = list(str(list_group[1].text).split("\n"))
                adr = "Москва, " + a[1].strip()
                metro = [a[0][a[0].find(" "):].strip()]
                

                # Pics
                images = offer_page.find_all("img", class_="img-responsive center-block")
                images = ["http://rentooki.ru"+x["src"] for x in images]


                # Group parsed data
                offer = {
                    "url": "http://rentooki.ru"+link,
                    "room_num": room_number,
                    "area": area,
                    "floor": floor,
                    "cost": cost,
                    "contacts": {"phone": contact_phone},
                    "metro": metro,
                    "pics": images,
                    "date": dt.strftime("%d.%m.%Y"),
                    "adr": adr,
                    "descr": descr
                }

                from pprint import pprint
                pprint(offer['url'])

                p.append(offer)
                #del p

            except:
                alertExc()
                pass


            # Next page on next iteration
            page_index += 1
            p.write_status(page_index)
            del p

    
    p = Parse('rentooki')
    p.add_date()
    del p


#===================================SDAM BEZ POSREDNIKOV=============================


def bez_posrednikov(maxprice):

    url = dict()
    #maxprice = '15000'
    p = Parse('bezPosrednikov')

    url['owners table'] = 'http://snimi-bez-posrednikov.ru/' \
                    'snyat-kvartiru?' \
                    'price=%s&' \
                    'tip[0]=квартира&' \
                    'komnat[0]=1&' \
                    'komnat[1]=2&' \
                    'komnat[2]=3&' \
                    'page=' % maxprice
    url['renters table'] = 'http://snimi-bez-posrednikov.ru/' \
                     'snimu-kvartiru?' \
                     'field_price_value=%s&' \
                     'field_tip_value[0]=квартира&' \
                     'komnat[0]=1&' \
                     'komnat[1]=2&' \
                     'komnat[2]=3&' \
                     'page=0' % maxprice

    url['home'] = 'http://snimi-bez-posrednikov.ru'
    url['buy'] = '/snyat-kvartiru?'
    url['sell'] = '/snimu-kvartiru?'
    url['price'] = 'price='
    url['flat'] = 'tip[0]=квартира'
    url['rooms_amount'] = 'komnat[0]='
    url['metro'] = 'metro='
    url['page'] = 'page='

    url['daiy'] = 'snyat-posutochno'


    def parseOwner(advert_url):
        print(url['home'] + advert_url)

        html = requests.get(url['home'] + advert_url).text
        soup = BeautifulSoup(html, 'html5lib')
        #print(soup, '------------------------')
        content = soup.find('div', {'class': 'node-content'})
        #print(content, '-----------------------')
        content = content.find('div', {'id': 'node-obyavlenie-full-group-content'})
        #print(content, '----------------------')

        rooms_amount = content.find('section', {'class': 'field field-name-field-komnat field-type-list-text field-label-inline clearfix view-mode-full'})
        if not (rooms_amount is None):
            rooms_amount = rooms_amount.find('div', {'class': 'field-item even'})
            rooms_amount = int(rooms_amount.text)

        subway = content.find('section', {'class': 'field field-name-field-metro field-type-taxonomy-term-reference field-label-inline clearfix view-mode-full'})
        if not (subway is None):
            subway = subway.find('li', {'class': 'field-item even'})
            subway = subway.text

        to_subway = content.find('section', {'class': 'field field-name-field-min-do-metro field-type-number-integer field-label-inline clearfix view-mode-full'})
        if not (to_subway is None):
            to_subway = to_subway.find('div', {'class': 'field-item even'})
            to_subway = to_subway.text

        adress = content.find('section', {'class': 'field field-name-field-adress field-type-text field-label-inline clearfix view-mode-full'})
        if not (adress is None):
            adress = adress.find('div', {'class': 'field-item even'})
            adress = adress.text

        description = content.find('div', {'class': 'field field-name-body field-type-text-with-summary field-label-hidden view-mode-full'})
        if not (description is None):
            description = description.find('div', {'class': 'field-item even'})
            description = description.text

        features = content.find('section', {'class': 'field field-name-field-osobennosti field-type-list-text field-label-inline clearfix view-mode-full'})
        if not (features is None):
            features = features.find('div', {'class': 'field-item even'})
            features = features.text

        full_square = content.find('section', {'class': 'field field-name-field-ploshad field-type-number-decimal field-label-inline clearfix view-mode-full'})
        if not (full_square is None):
            full_square = full_square.find('div', {'class': 'field-item even'})
            full_square = full_square.text.split()
            full_square = int(full_square[0])

        kitchen_square = content.find('section', {'class': 'field field-name-field-kuhnya field-type-number-decimal field-label-inline clearfix view-mode-full'})
        if not (kitchen_square is None):
            kitchen_square = kitchen_square.find('div', {'class': 'field-item even'})
            kitchen_square = kitchen_square.text.split()
            kitchen_square = int(kitchen_square[0])

        price = content.find('section', {'class': 'field field-name-field-price field-type-number-integer field-label-inline clearfix view-mode-full'})
        if not (price is None):
            price = price.find('div', {'class': 'field-item even'})
            price = price.text.split()
            price = int(price[0]) * 1000 + int(price[1])

        contacts = content.find('section', {'class': 'field field-name-field-tel field-type-text field-label-inline clearfix view-mode-full'})
        if not (contacts is None):
            contacts = contacts.find('div', {'class': 'field-item even'})
            contacts = contacts.text

        photos_ = content.find('div', {'class': 'field field-name-field-foto field-type-image field-label-hidden view-mode-full'})
        photos = list()
        if not (photos_ is None):
            photos_ = photos_.find('div', {'class': 'field-items'})
            for a in photos_:
                photos.append(a.a['href'])


        #print('FINISH; PRICE = %d' % price)
        #print(full_square)
        #print(rooms_amount, to_subway, subway)

        flat = dict()
        flat['room_num'] = rooms_amount
        flat['metro'] = subway
        flat['to_subway'] = to_subway
        flat['adr'] = adress
        flat['descr'] = description
        flat['features'] = features
        flat['area'] = full_square
        flat['kitchen_square'] = kitchen_square
        flat['cost'] = price
        flat['contacts'] = {'phone': contacts}
        flat['pics'] = photos
        flat['url'] = advert_url

        return flat


    # Здесь я начал переписывать по красоте parseOwnerList, но так и не закончил; вроде как здесь есть какая-то бага:

    # def parseOwnerList(rooms_amount, max_price):
    #     current_url = '%s%d%s%d' % (url['home'] + url['buy'] + url['price'], max_price, '&' + url['flat'] + '&' + url['rooms_amount'], rooms_amount)
    #     print(current_url)
    #
    #     try:
    #         html = requests.get(current_url).text
    #     except:
    #         print('Whoops! Somethind went wrong. Error 1')
    #         return None
    #
    #     soup = BeautifulSoup(html, 'html5lib')
    #
    #     pages = soup.find('li', {'class': 'pager-current odd'})
    #     pages = pages.text.split()
    #     pages = int(pages[2])
    #
    #     for page in range(pages + 1):
    #
    #         try:
    #             full_url = '%s%d' % (current_url + '&' + url['page'], page)
    #             print(full_url)
    #             html = requests.get(full_url).text
    #         except:
    #             print('Whoops! Somethind went wrong. Error 2')
    #             return None
    #
    #         soup = BeautifulSoup(html, 'html5lib')
    #         advert_table = soup.find('table', {'class': 'views-table cols-0'}).tbody
    #
    #         if (advert_table is None):
    #             print('Whoops! Somethind went wrong. Error 3')
    #             return None
    #
    #         for tr in advert_table:
    #             advert_url = tr.a['href']
    #
    #             if not (url['daiy'] in advert_url):
    #                 flat = parseOwner(advert_url)
    #                 print('price = %d, rooms = %d' % (flat['price'], flat['rooms_amount']))



    def parseOwnerList():
        try:
            html_pages = requests.get(url['owners table'] + '0').text
        except:
            print('Whoops! Somethind went wrong. Error 1')
            return None

        soup_pages = BeautifulSoup(html_pages, 'html5lib')
        pages = soup_pages.find('li', {'class': 'pager-current odd'})
        pages = pages.text.split()
        pages = int(pages[2])


        for page in range(pages + 1):

            print(' Page %d:' % page)
            p.write_status(page)
            #print(url['owners table'] + str(page))

            try:
                #html = requests.get(url_start + str('page') + url_end).text
                full_url = '%s%d' % (url['owners table'], page)
                #full_url = url['owners table'] + str(page)
                print(full_url)
                html = requests.get(full_url).text
            except:
                print('Whoops! Somethind went wrong. Error 2')
                return None

            soup = BeautifulSoup(html, 'html5lib')

            #===========--------------
            pages2 = soup.find('li', {'class': 'pager-current odd'})
            pages2 = pages2.text.split()
            print(pages2)
            pages2 = int(pages2[0])
            #===========---------------

            advert_table = soup.find('table', {'class': 'views-table cols-0'}).tbody

            if (advert_table is None):
                print('Whoops! Somethind went wrong. Error 3')
                return None

            for tr in advert_table:
                advert_url = tr.a['href']

                if not (url['daiy'] in advert_url):
                    flat = parseOwner(advert_url)
                    flat['date'] = tr.find('div', {'class': 'date'}).text
                    flat['loc'] = ""
                    p.append(flat)
                    #print(flat['price'])
                    #print('price = %d, rooms = %d' % (flat['price'], flat['rooms_amount']))
                    #print(str(flat))


    parseOwnerList()
    p.add_date()
    del p


#================================================VK=================================================#

def vk(n):        

    def picsarr(offer):
        parr = []
        try:
            pics = offer['attachments']
            #print(len(pics))
            for pic in pics:
                if pic['type'] == "photo":
                    picurl = pic['photo']['src_big']
                    parr.append(picurl)
        except:
            #alertExc()
            pass
        return parr


    def parse_vk_community(community, n):


        def getVkId(offer):
            vkid = offer['from_id']
            if vkid < 0:
                return "http://vk.com/club"+str(-vkid)
            return "http://vk.com/id"+str(vkid)
                
        
        counter = 0
        c = community['id']
        p = Parse(community['name'])
        for i in range(0, n, 100):
            offset = str(i)
            adr = "https://api.vk.com/method/wall.get?owner_id=-%s&count=100&filter=all&access_token=732c7b09732c7b09732c7b090673709b7f7732c732c7b092a6093eafb623ad5547f142f&offset=%s" % (c, offset)
            print(adr)
            offers = json.loads(requests.get(adr).text)
            offers = offers['response']
            for offer in offers[1:]:
                try:
                    counter += 1
                    p.write_status(counter)
                    p.append({'date': str(strftime("%Y-%m-%d %H:%M:%S", gmtime(offer['date']))), 'cost': 0, 'room_num': 0, 'area': 0, 'contacts': {'phone': '---', 'vk': getVkId(offer)}, 'pics': picsarr(offer), 'descr': offer['text'], 'metro': ['---'], 'url': "https://vk.com/wall-%s_%s" % (c, str(offer['id'])), 'loc': ["---"], 'adr': 'no_adress'})
                except Exception as e:
                    alertExc()
                    pass
        p.add_date()
        del p

    
    COMMUNITIES = [{'id': '1060484', 'name': "sdamsnimu"}, {'id': '29403745', 'name': "sdatsnyat"}, {'id': '62069824', 'name': "rentm"}, {'id': '49428949', 'name': "novoselie"}]
    
    for community in COMMUNITIES:
        #threading.Thread(target=parse_vk_community, args=(community, n,)).start()
        parse_vk_community(community, n)
        print("!!!!!!!!!!!!!1NOW WE PARSE",community)

    
#===========================================OPTIMIZATION============================================#

@tgExcCatch
def parse_it(name, maxprice):
    #print("!!!!!!!!!!!!!!!!!!!!!!!!!", name)
    if name == 'cian':
        cian(maxprice)
    elif name == 'realEstate':
        realestate(maxprice)
    elif name == 'kvartirant':
        kvartirant_room()
        #alertBot.sendMessage("ROOOM STAGE FINISHED!")
        kvartirant(maxprice)
    elif name == 'rentooki':
        parse_rentookiru(maxprice)
    elif name == 'bezPosrednikov':
        bez_posrednikov(maxprice)
    elif name == 'vk':
        vk(maxprice)

    BackuppedFile('parseRes.db').upload()
    

