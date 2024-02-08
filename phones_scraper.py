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
            result = json_read("result.json")
            if len(PROXY_LIST) < 1:
                logging.info("Все прокси заблокированы, добавьте новые")
                FL = False
                return
            proxy_num = rnd.randint(0, len(PROXY_LIST) - 1)
            current_proxy = PROXY_LIST[proxy_num]

            proxy = {
                "https": "http://" + current_proxy,
                "http": "http://" + current_proxy
            }

            session = requests.session()

            res = session.get(
                url=url,
                headers=HEADERS,
                proxies=proxy
            )

            soup = BeautifulSoup(res.text, "lxml")

            phone_token = soup.find(class_="object-page__popup-phone-btns").find('a').get('data-token')
            ID = soup.find(id='vue-app-object').get('data-id')
            if ID in result.keys():
                FL = False
                break
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

                result.update({ID: row_data})
                json_save(result, "result")

                FL = False

            elif cnt == 3:
                FL = False
                PROXY_LIST.pop(proxy_num)
                logging.info("Не удалось получить телефон. Проверьте прокси!")
            else:
                cnt += 1
    logging.info(f"Времени затрачено на одну страницу: {time.time() - start_time}")


def parse_phones():
    logging.info("Начинаем парсить телефоны")

    if not os.path.isfile("result.json"):
        json_save({}, "result")

    list = os.listdir("raw_json")

    for json in list:
        res = parse(json)
        if res is None:
            return

    logging.info("Все телефоны получены")


logging.basicConfig(level=logging.INFO, filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

