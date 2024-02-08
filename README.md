1)  Добавьте свои прокси в файл proxy.txt в виде {login}:{password}@{host}:{port}
    
(https://app.asocks.com) предоставляют достаточно большой пробный период
2) Для парсинга используется сервис https://rucaptcha.com необходимо зарегистрироваться и получить api ключ, после чего вставить его в файл config.py в графу captcha_key
3) Для запуска парсера введите след команды

        pip install -r requirements

        python main.py