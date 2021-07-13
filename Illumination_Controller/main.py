import requests
import json
from threading import Thread
import time
from datetime import date


def illumination_generator():
    while True:
        with open('settings.json') as file:
            json_data = json.load(file)
            file.close()
        if json_data['date'] == date.today() and json_data['time'] < 1:
            json_data['illumination'] = 0
            settings = requests.get('http://localhost:8000/api/logs/setLog?' + json_data['uuid'] + '&value=' + json_data['illumination']).json()
            json_data['refresh'] = settings['refresh']
        elif json_data['date'] != date.today() and json_data['time'] < 1:
            json_data['illumination'] = 1
            settings = requests.get('http://localhost:8000/api/logs/setLog?' + json_data['uuid'] + '&value=' + json_data['illumination']).json()
            json_data['time'] = settings['sec'] - settings['refresh']
            json_data['refresh'] = settings['refresh']
        elif json_data['date'] != date.today() and json_data['time'] > 0:
            json_data['illumination'] = 1
            settings = requests.get('http://localhost:8000/api/logs/setLog?' + json_data['uuid'] + '&value=' + json_data['illumination']).json()
            json_data['refresh'] = settings['refresh']
            json_data['time'] = json_data['time'] - settings['refresh']
            if json_data['time'] < 1:
                json_data['date'] = date.today()
        with open('settings.json', 'w') as f1:
            f1.write(json.dumps(json_data, ensure_ascii=False, indent=4))
            f1.close()
        time.sleep(json_data['refresh'])


def write_uuid(json_data, uuid):
    json_data['uuid'] = uuid
    with open('settings.json', 'w') as f:
        f.write(json.dumps(json_data, ensure_ascii=False, indent=4))


def connection(json_data):
    if json_data['uuid'] == "":
        data = requests.get('http://localhost:8000/api/devices/init?type=2').json()
        write_uuid(json_data, data['uuid'])


def main():
    # читаем json файл
    with open('settings.json') as file:
        json_data = json.load(file)
    # отправляем на сервер запрос для получения uuid, если его нет в json файле
    connection(json_data)
    # запускаем поток генерации данных датчика освещения
    # полученые значения с датчика записываем в json файл и отправляем запросом на сервер
    generator_thread = Thread(target=illumination_generator)
    generator_thread.start()


if __name__ == '__main__':
    main()
