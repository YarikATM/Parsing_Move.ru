
with open('proxy.txt') as f:
    PROXIES = [line.strip() for line in f.readlines()]


URL = "https://sverdlovsk.move.ru/ekaterinburg/kvartiry/ot_sobstvennika/ot_agentstv/vtorichnaya/"

HEADERS = {
    'authority': 'sverdlovsk.move.ru',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru,en;q=0.9',
    'cache-control': 'no-cache',
    # 'cookie': 'move_segment_ssr_blocks_2=-1; PHPSESSID=b0c03dada0ab2ff54fb6584112d8d0be; movea=66; portal_client_id=5e5d63479c16ad04e82e9bd756fca6e077283004; region=NaN; _ga=GA1.1.1642819798.1706433156; moveb=218218%2C74594; showslidebanner=1; _ym_uid=1706433157245781257; _ym_d=1707325055; tmr_lvid=eb4484ba2eea8bac9808589ebdd1cd69; tmr_lvidTS=1707325055195; _ym_isad=2; move_looks_search_items=25; _ga_JG51WTKJG4=GS1.1.1707327248.14.0.1707327248.0.0.0; _ym_visorc=b; tmr_detect=0%7C1707327250940',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Chromium";v="118", "YaBrowser";v="23.11", "Not=A?Brand";v="99", "Yowser";v="2.5"',
    'Sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36',
}


POST_HEADERS =  {
    'authority': 'sverdlovsk.move.ru',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'ru,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'cookie': 'move_segment_ssr_blocks_2=-1; PHPSESSID=b0c03dada0ab2ff54fb6584112d8d0be; movea=66; portal_client_id=5e5d63479c16ad04e82e9bd756fca6e077283004; region=NaN; _ga=GA1.1.1642819798.1706433156; moveb=218218%2C74594; showslidebanner=1; _ym_uid=1706433157245781257; _ym_d=1707325055; tmr_lvid=eb4484ba2eea8bac9808589ebdd1cd69; tmr_lvidTS=1707325055195; _ym_isad=2; move_looks_search_items=27; _ym_visorc=w; _ga_JG51WTKJG4=GS1.1.1707383707.15.1.1707385456.0.0.0; tmr_detect=0%7C1707385459882',
    'origin': 'https://sverdlovsk.move.ru',
    'pragma': 'no-cache',
    'referer': 'https://sverdlovsk.move.ru/objects/ekaterinburg_ulica_narodnoy_voli_d_52_6916567485/',
    'sec-ch-ua': '"Chromium";v="118", "YaBrowser";v="23.11", "Not=A?Brand";v="99", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}


captcha_key = "e4a4ea151a792a3ce4de02cfdee5dabd"