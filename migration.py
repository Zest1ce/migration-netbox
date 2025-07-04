from typing import List, Dict, Optional
from datetime import datetime
from collections import Counter
from json.decoder import JSONDecodeError
from progress.bar import IncrementalBar
from transliterate import translit
import re
import requests
import json
import ssl
import urllib3
import ipaddress
import backoff
import logging
import certifi
import ssl
import os
import sys
# Отключение уведомлений о небезопасных способах подключения к API 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Настройки для phpIPAM
from credential import PHPIPAM_URL, PHPIPAM_APP_ID, PHPIPAM_API_TOKEN, NETBOX_URL, NETBOX_API_TOKEN
start_time = datetime.now()
# Хедеры для API запросов
HEADERS_PHPIPAM = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'token': PHPIPAM_API_TOKEN
}
HEADERS_NETBOX = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Token {NETBOX_API_TOKEN}'
}
#
counter = Counter(ipaddr=0, pref=0)
# Настройка логирования
log_file_path = "./data/script_logs.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=log_file_path,  # Указываем файл для записи логов
    filemode="a",  # Режим записи: "a" - добавлять в файл, "w" - перезаписывать файл
)
# Открываем файл для записи логов
log_file = open(log_file_path, "a")  # "a" для добавления логов в конец файла
# Перенаправляем выводы
sys.stdout = log_file  # Все print будут писать в файл
sys.stderr = log_file  # Все ошибки будут писать в файл
# Проверка соединения с API phpIPAM и NetBOX
from api_health_check import check_phpipam_connection, check_netbox_connection
# GET запрос к phpIPAM на получение подсетей
from get_phpipam_subnets import get_phpipam_subnets
# GET запрос к phpIPAM на получение адресов
from get_phpipam_addresses import get_phpipam_addresses
# GET запрос к phpIPAM на получение VLANs
from get_phpipam_vlans import get_phpipam_vlans
# GET запрос к phpIPAM на получение Devices
from get_phpipam_devices import get_phpipam_devices
# Функция для получения типа Devices
from get_phpipam_devices_type import get_phpipam_devices_type
# Функция для открытия разных json файлов
from load_data_from_json import load_data_from_json
# Генерация ссылок для NetBOX из названий в phpIPAM (русские символы в латиницу)
from clean_slug import clean_slug
# Создание локации из данных phpIPAM в NetBOX
from create_site_in_netbox import create_site_in_netbox
# Создание VLANs из данных phpIPAM в NetBOX
from create_vlan_in_netbox import create_vlan_in_netbox
# Перенос подсетей с локацией и vlan(Обработчик для запросов из phpIPAM в NetBOX) 
from create_subnets_in_netbox import create_subnets_in_netbox
# Перенос IP адрессов(Обработчик для запросов из phpIPAM в NetBOX) 
from create_addresses_in_netbox import create_addresses_in_netbox
# Перенос девайсов(Обработчик для запросов из phpIPAM в NetBOX) 
from create_devices_in_netbox import create_devices_in_netbox
# Генерация файла локаций с id 
from generate_location_json import generate_location_json


def main_function():
    # Запуск функций проверки коннекта к API
    check_phpipam_connection('sections')
    check_netbox_connection('status')
    # Запуск функции запроса к phpIPAM для получения подсетей и сохранение json файла
    subnets_data = get_phpipam_subnets('subnets')
    if subnets_data:
        # Сохранение данных в файл JSON с отступами для читаемости
        with open("./data/phpipam_data_subnet.json", "w", encoding="utf-8") as json_file:
            json.dump(subnets_data, json_file, ensure_ascii=False, indent=4)
        print("Данные успешно сохранены в файл phpipam_data_subnet.json")
    else:
        print("Не удалось получить данные из phpIPAM.")
    # Запуск функции запроса к phpIPAM для получения ip адресов и сохранение json файла
    addresses_data = get_phpipam_addresses('addresses/all')
    if addresses_data:
        # Сохранение данных в файл JSON с отступами для читаемости
        with open("./data/phpipam_data_addresses.json", "w", encoding="utf-8") as json_file:
            json.dump(addresses_data, json_file, ensure_ascii=False, indent=4)
        print("Данные успешно сохранены в файл phpipam_data_addresses.json")
    else:
        print("Не удалось получить данные из phpIPAM.")
    # Запуск функции запроса к phpIPAM для получения VLAN и сохранение json файла
    vlans_data = get_phpipam_vlans('vlan/all')
    if vlans_data:
        # Сохранение данных в файл JSON с отступами для читаемости
        with open("./data/phpipam_data_vlans.json", "w", encoding="utf-8") as json_file:
            json.dump(vlans_data, json_file, ensure_ascii=False, indent=4)
        print("Данные успешно сохранены в файл phpipam_data_vlans.json")
    else:
        print("Не удалось получить данные из phpIPAM.")
    # Запуск функции запроса к phpIPAM для получения VLAN и сохранение json файла
    devices_data = get_phpipam_devices('devices/all')
    if devices_data:
        # Сохранение данных в файл JSON с отступами для читаемости
        with open("./data/phpipam_data_devices.json", "w", encoding="utf-8") as json_file:
            json.dump(devices_data, json_file, ensure_ascii=False, indent=4)
        print("Данные успешно сохранены в файл phpipam_data_devices.json")
    else:
        print("Не удалось получить данные из phpIPAM.")
    # Запуск функции создания json для локации по данным из выгрузки подсетей
    locations_data = generate_location_json()
    if locations_data:
        # Сохранение данных в файл JSON с отступами для читаемости
        with open("./data/phpipam_data_location.json", "w", encoding="utf-8") as json_file:
            json.dump(locations_data, json_file, ensure_ascii=False, indent=4)
        print(f"Данные успешно сохранены в phpipam_data_location.json")
    else:
        print("Не удалось получить данные из phpIPAM.")
    # Запуск обработчика json
    create_subnets_in_netbox()
    create_addresses_in_netbox()
    create_devices_in_netbox()

main_function()

print(f"Исполнение скрипта заняло: {datetime.now() - start_time}")
print("_____________________________________________________________________________________________________________________")