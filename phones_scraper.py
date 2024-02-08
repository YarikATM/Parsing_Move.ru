import json
import os
import time
import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
from config import PROXIES, HEADERS, POST_HEADERS
import requests
import random

rnd = random.Random()


def json_save(data, path):
    with open(f'{path}.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def json_read(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.load(f)


PROXY_LIST = PROXIES.copy()


def parse(name):
    data = json_read(f"raw_json/{name}")

    urls_to_parse = []
    c = 0
    for key in data.keys():
        params = data[key]
        url = params["url"]
        urls_to_parse.append(url)
        c += 1

    start_time = time.time()
    for url in urls_to_parse:

        FL = True
        cnt = 0
        while FL:
            res = json_read("result.json")

            current_proxy = PROXY_LIST[rnd.randint(0, len(PROXY_LIST) - 1)]

            proxy = {
                "https": "http://" + current_proxy
            }

            session = requests.session()

            res = session.get(
                url=url,
                headers=HEADERS,

            )

            soup = BeautifulSoup(res.text, "lxml")

            phone_token = soup.find(class_="object-page__popup-phone-btns").find('a').get('data-token')
            ID = soup.find(id='vue-app-object').get('data-id')
            if ID in res.keys():
                FL = False
            post_res = session.post(
                url="https://sverdlovsk.move.ru/ajax/items_v3/get_item_phone",
                data={"token": phone_token},
                headers=POST_HEADERS,
                proxies=proxy

            ).json()

            if post_res["status"] == 1:
                row_data = data[ID]

                row_data["phones"] = post_res["data"]["phones"]
                del row_data["url"]
                logging.info(f"Телефон получен: {post_res['data']['phones']}")

                res.update({ID: row_data})
                json_save(res, "result")

                FL = False

            elif cnt == 3:
                FL = False
                logging.info("Не удалось получить телефон. Проверьте прокси!")
            else:
                cnt += 1
    logging.info(f"Времени затрачено на одну страницу: {time.time() - start_time}")


def parse_phones():
    logging.info("Начинаем парсить телефоны")

    if not os.path.isfile("result.json"):
        json_save({}, "result")

    list = os.listdir("raw_json")

    for json in list[:1]:
        parse(json)

    logging.info("Все телефоны получены")
