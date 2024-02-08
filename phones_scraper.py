import json
import os
import time
import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
from config import PROXIES, HEADERS, POST_HEADERS, captcha_key
import requests
import random
from fake_useragent import UserAgent

ua = UserAgent()
rnd = random.Random()


def json_save(data, path):
    with open(f'{path}.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def json_read(path):
    with open(path, 'r', encoding="utf-8") as f:
        return json.load(f)


PROXY_LIST = PROXIES.copy()


async def solve_captcha(session: aiohttp.ClientSession, url, captcha_token, phone_token, proxy):
    try:
        async with session.get(
                url=f"http://rucaptcha.com/in.php?key={captcha_key}&method=userrecaptcha&googlekey={captcha_token}&pageurl={url}&json=1"
        ) as response:
            res = await response.json()


        request_id = res["request"]

        await asyncio.sleep(20)

        while True:
            await asyncio.sleep(7)

            async with session.get(
                url=f"http://rucaptcha.com/res.php?key={captcha_key}&action=get&id={request_id}&json=1"
            ) as response:
                result_captcha = await response.json()



            if result_captcha["status"] == 1:
                break

        recaptha_response = result_captcha["request"]


        async with session.post(
            url=f"https://sverdlovsk.move.ru/captcha/phone/",
            data={
                "token": phone_token,
                "g-recaptcha-response": recaptha_response
            }, proxy=proxy
        ) as response:
            res = await response.json(content_type='text/html')


        async with session.post(url="https://sverdlovsk.move.ru/ajax/items_v3/get_item_phone",
                                data={"token": phone_token},
                                headers=POST_HEADERS,
                                proxy=proxy) as response:
            post_res = await response.json(content_type='text/html')


        if post_res["status"] == 1:
            return post_res["data"]["phones"]
    except Exception as e:
        logging.error(str(e))




async def create_tasks(url_list: list):
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ttl_dns_cache=300)) as session:
            tasks = []
            for url in url_list:
                task = asyncio.create_task(get_phone(session, url))
                tasks.append(task)

            return await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(" | " + str(e))


async def get_phone(session: aiohttp.ClientSession, url):
    try:
        current_proxy = PROXY_LIST[rnd.randint(0, len(PROXY_LIST)-1)]
        proxy = "http://" + current_proxy
        async with session.get(url=url, headers=HEADERS) as response:
            res = await response.text()

        soup = BeautifulSoup(res, "lxml")

        captcha_token = ''
        scripts = soup.findAll("script")
        for s in scripts:
            if "RECAPTCHA" in s.text:
                captcha_token = s.text.split('", "')[1].split('"')[0]

        phone_token = soup.find(class_="object-page__popup-phone-btns").find('a').get('data-token')
        ID = soup.find(id='vue-app-object').get('data-id')

        async with session.post(url="https://sverdlovsk.move.ru/ajax/items_v3/get_item_phone",
                                data={"token": phone_token},
                                headers=POST_HEADERS,
                                proxy=proxy) as response:
            post_res = await response.json(content_type='text/html')

        logging.debug(post_res)
        if post_res["status"] == 1:
            phones = post_res["data"]["phones"]
            return (ID, phones)
        elif post_res["status"] == 2:
            phones = await solve_captcha(session, url, captcha_token, phone_token, proxy)
            return (ID, phones)

    except:
        pass


def parse_captcha(name):
    data = json_read(f"raw_json/{name}")

    urls_to_parse = []
    c = 0
    for key in data.keys():
        params = data[key]
        url = params["url"]
        urls_to_parse.append(url)
        c += 1

    start_time = time.time()

    result = []
    lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
    list_urls_to_parse = lol(urls_to_parse, 20)
    for urls_list in list_urls_to_parse:
        list_of_phones = asyncio.run(create_tasks(urls_list))

        for i in list_of_phones:
            if i is None:
                continue

            ID = i[0]
            phones = i[1]
            if phones is not None:
                page = data[ID]
                del page["url"]
                page["phones"] = phones
                result.append(page)

    logging.info(f"Получены номера с {name}, времени затрачено: {time.time() - start_time}")
    return result



def parse_phones():
    logging.info("Начинаем парсить телефоны")
    json_save([], "result")

    list = os.listdir("raw_json")

    for json in list:
        data = json_read("result.json")
        res = parse_captcha(json)
        data.extend(res)
        json_save(data, "result")

    logging.info("Все телефоны получены")


logging.basicConfig(level=logging.INFO, filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


if __name__ == "__main__":
    parse_phones()