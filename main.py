import random
import validators
import logging
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time
import json
import datetime
import os, os.path
import locale
from phones_scraper import parse_phones
from config import URL, PROXIES, HEADERS
from fake_useragent import UserAgent
ua = UserAgent()
rnd = random.Random()


if not os.path.isdir("raw_json"):
    os.mkdir("raw_json")



def normalize_time(publication_date: str):
    publication_date = publication_date.replace("декабря", "12").replace("октября", "10").replace("февраля", "2")\
        .replace("января", "1").replace("марта", "3").replace("апреля", "4").replace("мая", "5")\
        .replace("июня", "6").replace("июля", "7").replace("августа", "8").replace("сентября", "9")\
        .replace("ноября", "11")
    if "сегодня в" in publication_date:

        publication_date = publication_date.replace("сегодня в ", "2024-01-30T") + ":00Z"
        # print(publication_date)
    elif "вчера в " in publication_date:
        publication_date = publication_date.replace("вчера в ", "2024-01-29T") + ":00Z"

    elif "2021" in publication_date or "2019" in publication_date or "2022" in publication_date \
            or "2023" in publication_date or "2020" in publication_date or "2018" in publication_date \
            or "2017" in publication_date:
        # print(publication_date)
        publication_date = datetime.datetime.strptime(publication_date, "%d %m %Y")
        publication_date = str(publication_date).replace(" ", "T") + "Z"

        # print(publication_date)
    else:
        # print(publication_date)
        publication_date = datetime.datetime.strptime(publication_date, "%d %m")
        publication_date = str(publication_date).replace(" ", "T").replace("1900", "2024") + "Z"
        # print(publication_date)
        pass

    if publication_date[0] == "2" and publication_date[4] == "-" and publication_date[7] == "-" \
            and publication_date[10] == "T" and publication_date[-4] == ":" and publication_date[-7] == ":" \
            and publication_date[-1] == "Z":

        # print(publication_date)
        pass
    else:
        logging.error(f"Ошибка в получении даты: {publication_date}")

    return publication_date


async def load_page(urls: list):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ttl_dns_cache=300)) as session:
            tasks = []
            for url in urls:
                task = asyncio.create_task(get_page(session, url))
                tasks.append(task)

            return await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(" | " + str(e))


async def get_page(session: aiohttp.ClientSession, url):
    while True:

        rand = rnd.randint(0, len(PROXIES) - 1)
        current_proxy = "http://" + PROXIES[rand]
        HEADERS["user-agent"] = ua.random

        try:
            async with session.get(url=url, headers=HEADERS,
                                   # proxy=current_proxy,
                                   ssl=False) as response:

                data = await response.text()
                assert response.status == 200


                return BeautifulSoup(data, "lxml")

        except AssertionError as e:
            print(f"Прокси заблокирован. Пробуем следующий прокси... | {str(e)}")

        except aiohttp.ClientProxyConnectionError:
            print(f'Ошибка подключения к прокси {current_proxy}. Пробуем следующий прокси...')

        except Exception as e:
            logging.error("Проверьте прокси" + str(e))


async def get_pagination() -> int:
    logging.info("Getting pagination count")

    url = "https://sverdlovsk.move.ru/ekaterinburg/kvartiry/ot_sobstvennika/ot_agentstv/vtorichnaya/?limit=100"
    page = await load_page([url])


    pagination = int(page[0].find(class_="pagination-block__list").findAll("li")[-1].text.strip())



    logging.info(f"find {pagination} pages")

    return pagination


def get_apartments_urls(soup: BeautifulSoup) -> list[str]:
    result = []

    res = soup.find("div", id="vue-app-items").find(class_="enshrined-items").find_parent().findAll(
        class_="search-item move-object")

    base_url = "https://sverdlovsk.move.ru/objects/"

    for div in res:
        href = div.find(class_='search-item__image-block').find('a').get('href').split('/')[-2]
        result.append(base_url + href)
    return result






def parse_apartments_data(soup: BeautifulSoup):
    row_obj = {}
    obj = {}
    apartment_params = {}

    id = soup.find(id='vue-app-object').get('data-id')
    obj["id"] = int(id)

    # тип продавца(собственник; риелтор; сторонний и тд)
    if soup.find(class_="block-user__agency") is not None:
        seller_type = soup.find(class_="block-user__agency").text.strip()
        obj["seller_type"] = seller_type

        # Имя в графе продавца объекта;
        seller_name = soup.find(class_="block-user__name").text.strip()
        obj["seller_name"] = seller_name

    url = "https:" + soup.find(id="object-button_toPdf").get("data-url")
    obj["url"] = url
    obj["phones"] = None
    # проверка на актуальность
    try:
        ch = soup.find("div", class_='block-user__name_blank').text.strip()
        if ch == "Объявление устарело":
            return "Устарело"
    except:
        pass



    #
    data = soup.find(class_="col-sm-12 col-md-8 col-lg-9 two-column__left")
    desc = data.find(class_="row").find(class_="col-xs-12 col-sm-7 col-md-12 col-lg-12").findAll(
        class_="object-info")

    apartment_block = None
    building_block = None

    for i in desc:
        h3 = i.find('h3').text.strip()
        match h3:
            case "Квартира в продажу":
                apartment_block = i
            case "Студия в продажу":
                apartment_block = i
            case "Информация о доме":
                building_block = i

    # Вкладка Квартира в продажу
    if apartment_block is not None:
        apartments = apartment_block.findAll(class_="col-xs-12 col-sm-12 col-md-6 col-lg-6")

        apart_block_1 = apartments[0].find('ul').findAll('li')
        apart_block_2 = apartments[1].find('ul').findAll('li')

        for row in apart_block_1:
            data = row.findAll('div')
            title = data[0].get('title')

            match title:
                case "Цена":
                    price = data[1].text.replace("₽", '').replace(' ', '').strip()
                    obj["price"] = int(price)
                case "Количество комнат":
                    room_cnt = int(data[1].text)
                    row_obj["room_count"] = room_cnt
                case "Тип объекта":
                    apart_type = data[1].text
                    row_obj["apart_type"] = apart_type
                case "Этаж":
                    floor = data[1].text.split("/")

                    apart_floor = int(floor[0])
                    floors_count = int(floor[1])

                    apartment_params["floor"] = apart_floor
                    apartment_params["count_of_floors"] = floors_count

        for row in apart_block_2:
            data = row.findAll('div')
            title = data[0].get('title')

            match title:
                case "Общая площадь":
                    total_area = float(data[1].text.split(" ")[0])
                    apartment_params["total_area"] = total_area
                case "Тип объекта":
                    apart_type = data[1].text
                    row_obj["apart_type"] = apart_type
                case "Жилая площадь":
                    living_area = float(data[1].text.split(" ")[0])
                    apartment_params["living_area"] = living_area
                case "Площадь кухни":
                    kitchen_area = float(data[1].text.split(" ")[0])
                    apartment_params["kitchen_area"] = kitchen_area
                case "Дата публикации":
                    publication_date = data[1].text
                    publication_date = normalize_time(publication_date)
                    obj["publication_date"] = publication_date
                case "Дата  обновления":
                    update_date = data[1].text
                    update_date = normalize_time(update_date)
                    obj["update_date"] = update_date

        if row_obj["apart_type"] == "студия":
            apartment_params["apart_type"] = "квартира-студия"
        elif row_obj["apart_type"] == "квартира":
            apartment_params["apart_type"] = f"{row_obj['room_count']}-комнатная квартира"

    # Вкладка Информация о доме
    if building_block is not None:
        building = building_block.find(class_='row object-info__row').find("div").find("ul").findAll("li")

        for row in building:
            data = row.findAll('div')
            title = data[0].get('title')
            match title:
                case "Год постройки":
                    year_of_building = int(data[1].text.split(" ")[0])
                    apartment_params["year_of_building"] = year_of_building
                case "Адрес":

                    address = data[1].text.strip().replace('\n', ' ')
                    obj["location"] = dict()
                    obj["location"]["address"] = address

    # Описание и информация
    text_block = soup.findAll(class_="object-page__header-object-block")
    for block in text_block:
        if block.text.strip() == "Описание":
            description = block.find_next().text
            apartment_params["description"] = description
        elif block.text.strip() == "Информация":
            additional_information = block.find_next().text
            apartment_params["additional_information"] = additional_information

    # Фотографии
    photo_urls = []
    row_photo_urls = soup.find(class_="images-slider specs").find("div").findAll(href=True)

    for url in row_photo_urls:
        photo_url = url.get("href")
        if not validators.url(photo_url):
            photo_url = "http:" + photo_url
        photo_urls.append(photo_url)

    apartment_params["photo_urls"] = photo_urls

    # Координаты
    raw_coordinates = soup.find(class_='images-slider specs').findAll('div')[-1].find_parent().get("data-img") \
        .split("=")[1].replace('&l', '').split(",")
    coordinates = [float(item) for item in raw_coordinates]
    obj["location"]["coordinates"] = coordinates

    obj["apartments_params"] = apartment_params

    return {id: obj}


def json_save(data, path):
    with open(f'{path}.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def json_read(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.load(f)


async def get_all_data(urls: list[str]):
    logging.info("Start requesting pages")
    main_soups = await load_page(urls)
    logging.info("Succesfully get all pages")

    all_start_time = time.time()
    for index, soup in enumerate(main_soups):
        start_time = time.time()
        page = index + 1
        r_data = None
        apartment_urls = get_apartments_urls(soup)
        urls_to_parse = []
        apart_data = {}

        if os.path.isfile(f"raw_json/{page}_page.json"):
            r_data = json_read(f"raw_json/{page}_page.json")
            apart_data = r_data

        if r_data is not None:
            for apart_url in apartment_urls:
                apart_id = apart_url.split("_")[-1]

                if r_data.get(apart_id) is None:
                    urls_to_parse.append(apart_url)
        else:
            urls_to_parse = apartment_urls
        if len(urls_to_parse) == 0:
            logging.info(f"Found scraped {page} page!")
            continue

        apartment_soups = await load_page(apartment_urls)

        for apart_soup in apartment_soups:
            data = parse_apartments_data(apart_soup)

            if data == "Устарело":
                logging.info("Найдено устаревшее объявление")
                logging.info(f"Времени затрачено на все страницы: {time.time() - all_start_time}")
                return

            if data is not None:
                apart_data.update(data)

            json_save(apart_data, f"raw_json/{page}_page")

        logging.info(f"Времени затрачено на парсинг страницы №{page}: {time.time() - start_time}")
    logging.info(f"Времени затрачено на все страницы: {time.time() - all_start_time}")


def get_pages_urls(pagination: int) -> list[str]:
    # pagination = 5
    urls = []
    for page in range(1, pagination + 1):
        url = URL + f"?page={page}&limit=100"
        urls.append(url)
    return urls


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    pagination = loop.run_until_complete(get_pagination())

    urls = get_pages_urls(pagination)

    loop.run_until_complete(get_all_data(urls))


    parse_phones()



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s")
    main()
