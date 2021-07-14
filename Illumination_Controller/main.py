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
        print('Настройки контроллера получены...')
        print(json_data)
        if json_data['date'] == str(date.today()) and json_data['time'] < 1:
            json_data['illumination'] = 0
            settings = requests.get('http://localhost:8000/api/logs/setLog?uuid=' + json_data['uuid'] + '&value=' + str(json_data['illumination'])).json()
            json_data['refresh'] = settings['refresh']
        elif json_data['date'] != str(date.today()) and json_data['time'] < 1:
            json_data['illumination'] = 1
            settings = requests.get('http://localhost:8000/api/logs/setLog?uuid=' + json_data['uuid'] + '&value=' + str(json_data['illumination'])).json()
            json_data['time'] = settings['sec'] - settings['refresh']
            json_data['refresh'] = settings['refresh']
            print('Контроллер выполняет отсвет...')
            print('Оставшееся время отсвета: ', settings['sec'], 'Время до обновления данных: ', settings['refresh'])
        elif json_data['date'] != str(date.today()) and json_data['time'] > 0:
            json_data['illumination'] = 1
            settings = requests.get('http://localhost:8000/api/logs/setLog?uuid=' + json_data['uuid'] + '&value=' + str(json_data['illumination'])).json()
            json_data['refresh'] = settings['refresh']
            json_data['time'] = json_data['time'] - settings['refresh']
            print('Оставшееся время отсвета: ', json_data['time'], 'Время до обновления данных: ', settings['refresh'])
            if json_data['time'] < 1:
                json_data['date'] = str(date.today())
                print('Установленное время отсвета истекло, контроллер ожидает начало следующего дня...')
        with open('settings.json', 'w') as f1:
            f1.write(json.dumps(json_data, ensure_ascii=False, indent=4))
            f1.close()
            print('Настройки контроллера обновлены...')
        time.sleep(json_data['refresh'])


def write_uuid(json_data, uuid):
    json_data['uuid'] = uuid
    with open('settings.json', 'w') as f:
        f.write(json.dumps(json_data, ensure_ascii=False, indent=4))
        f.close()


def connection(json_data):
    if json_data['uuid'] == "":
        print('Получение UUID контроллера с сервера впервые...')
        data = requests.get('http://localhost:8000/api/devices/init?type=2').json()
        print('UUID: ', data['uuid'])
        write_uuid(json_data, data['uuid'])
    else:
        print('UUID контроллера получен...')
        print('UUID: ', json_data['uuid'])


def main():
    print('Контроллер освещенности запущен...')
    with open('settings.json') as file:
        json_data = json.load(file)
        file.close()
    connection(json_data)
    print('Генерация данных контроллера запущена...')
    generator_thread = Thread(target=illumination_generator)
    generator_thread.start()


if __name__ == '__main__':
    main()