# This Python file uses the following encoding: utf-8

import re
import requests
import json
import time
import datetime
from bs4 import BeautifulSoup
from time import gmtime, strftime
from parser_class import Parse
from datetime import datetime, timedelta

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
    p.add_date() #я не умею эту фигню писать


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
        try:
            add = int(media.find('div', class_='obj-active-panel').find('div', class_='toogle-button').get('blst'))
            if add == 0:
                add = int(media.find('div', class_='obj-active-panel').find('div', class_='toogle-button').get('lst1'))
            add = str(add//17)[1:]  
            phone = media.find('div',class_='object-connect').find('div',class_='object-builder-phone_block').find('div', class_='object-builder-phone').text[:-3] + add
            print(phone)
            contacts['phone'] = phone
        except:
            contacts['phone'] = 'err'


        #loc

        loc = []

        return date, cost, descr, pics, room_num, area, adr, metro, contacts, loc

        #Location // Можно вытащить из названия объявления



    def get_total_pages(url):
        soup = BeautifulSoup(get_html(url), 'lxml')
        total_pages = soup.find('section', class_='clear-fix').find_all('div', class_='contentblock')[1].find('div', class_='main-content').find('div', class_='list-panel').find('div', class_='more-info').find_all('a')[-1].get('href').split('pg')[1][:-1]
        return int(total_pages)




    def realest(maxprice):
        p = Parse('realEstate')
        currentPage = 1
        template = 'http://www.realestate.ru'
        page_url_template = 'http://www.realestate.ru/flatrent/s/rcs10.1.2.3-rgs1.2.3.4.5.6.7.8.9.10-prt{0}/pg'.format(int(maxprice)//1000)#'http://www.realestate.ru/flatrent/pg'
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
                try:
                    url = template + ad.find('div', class_='obj-item').find('a').get('href')
                    #lat = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lat') # Получаем широту и долготу
                    #lng = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').get('lng') # скрытые в названии объявления
                    adr = ad.find('div', class_='obj-item').find('a', class_='obj-name house-Geoposition').text
                    html = get_html(url)
                    print(url)
                    date, cost, descr, pics, room_num, area, adr2, metro, contacts, loc = get_page_data(html)
                    data = {'date': date, 'cost': cost, 'descr': descr, 'pics':pics, 'room_num': room_num, 'area':area, 'adr':adr, 'metro': metro, 'url': url, 'loc': loc, 'contacts':contacts}
                    p.append(data)
                    #print(data)
                    p.write_status(currentPage)
                    print('Current page: %s' % currentPage)
                except Exception as e:
                    print(str(e), "BUT WE CONTINUE OPERATING")

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
        p = Parse('kvartirant')
        base_url = 'http://www.kvartirant.ru/bez_posrednikov/Moskva/sniat-kvartiru/'
        params = '&cost_limit={0}&komnat[]=1&komnat[]=2&komnat[]=3'.format(maxprice)
        template = 'http://www.kvartirant.ru'
        html = get_html(base_url)
        counter = 0
        # out = []
        total_pages = get_total_pages(html)
        for page in range(total_pages)[1:]:
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
                        print(str(e), "BUT WE CONTINUE OPERATING")
            # with open('text.txt', 'w', encoding='utf-8') as out_file:
            #   out_file.write(str(out))
            # break 

        print('Done!')
        p.add_date()
        #return out          


        # run
    kvartir(int(maxprice))


#===================================================================================================#


def parse_rentookiru(maxprice):

    # offers = []
    p = Parse('rentooki')
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
            break

        for link in links:
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
                room_number = int(re.match(r".+ (\d)-к ", offer_type_field).group(1))
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

            except Exception as e:
                print("Rukozhop EXCEPTION", str(e))
                pass


            # Next page on next iteration
            page_index += 1
            p.write_status(page_index)

    p.add_date()

    
#===========================================OPTIMIZATION============================================#

def parse_it(name, maxprice):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!11", name)
    if name == 'cian':
        cian(maxprice)
    elif name == 'realEstate':
        realestate(maxprice)
    elif name == 'kvartirant':
        kvartirant(maxprice)
    elif name == 'rentooki':
        parse_rentookiru(maxprice)
