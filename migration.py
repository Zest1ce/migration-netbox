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
# Проверка соединения с API phpIPAM
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def check_phpipam_connection(phpipam_api_endpoint):
    try:
        url = f"{PHPIPAM_URL}/{PHPIPAM_APP_ID}/{phpipam_api_endpoint}/" # Формируем URL для запроса данных по эндпоинту
        print(f"Проверка соединения по адресу: {url}")
        response = requests.get(url, 
                                headers=HEADERS_PHPIPAM, 
                                verify=False)
        if response.status_code == 200:
            print("Соединение с API phpIPAM успешно установлено.")
            return response.json()
        else:
            print(f"Ошибка при запросе данных: {response.status_code} - {response.reason}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к API phpIPAM: {error_api}")
# Проверка соединения с API NetBOX
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def check_netbox_connection(netbox_api_endpoint):
    try:
        url = f"{NETBOX_URL}/{netbox_api_endpoint}/" # Формируем URL для запроса данных по эндпоинту
        print(f"Проверка соединения по адресу: {url}")
        response = requests.get(url, 
                                headers=HEADERS_NETBOX, 
                                verify=False)
        if response.status_code == 200:
            print("Соединение с API NetBOX успешно установлено.")
            return response.json()
        else:
            print(f"Ошибка при запросе данных: {response.status_code} - {response.reason}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к API NetBOX: {error_api}")
# GET запрос к phpIPAM на получение подсетей
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def get_phpipam_subnets(phpipam_api_endpoint):
    try:
        url = f"{PHPIPAM_URL}/{PHPIPAM_APP_ID}/{phpipam_api_endpoint}/" # Формируем URL для запроса данных о секции
        print(f"Обработка запроса по эндпоинту: {url}")
        response = requests.get(url, headers=HEADERS_PHPIPAM, verify=False)

        if response.status_code == 200:
            print("Успешный запрос данных из phpIPAM.")
            return response.json()
        else:
            print(f"Ошибка при запросе данных: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к эндпоинту phpIPAM: {error_api}")
# GET запрос к phpIPAM на получение адресов
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def get_phpipam_addresses(phpipam_api_endpoint):
    try:
        url = f"{PHPIPAM_URL}/{PHPIPAM_APP_ID}/{phpipam_api_endpoint}/" # Формируем URL для запроса данных о секции
        print(f"Обработка запроса по эндпоинту: {url}")
        response = requests.get(url, headers=HEADERS_PHPIPAM, verify=False)

        if response.status_code == 200:
            print("Успешный запрос данных из phpIPAM.")
            return response.json()
        else:
            print(f"Ошибка при запросе данных: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к эндпоинту phpIPAM: {error_api}")
# GET запрос к phpIPAM на получение VLANs
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def get_phpipam_vlans(phpipam_api_endpoint):
    try:
        url = f"{PHPIPAM_URL}/{PHPIPAM_APP_ID}/{phpipam_api_endpoint}/" # Формируем URL для запроса данных о секции
        print(f"Обработка запроса по эндпоинту: {url}")
        response = requests.get(url, headers=HEADERS_PHPIPAM, verify=False)

        if response.status_code == 200:
            print("Успешный запрос данных из phpIPAM.")
            return response.json()
        else:
            print(f"Ошибка при запросе данных: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к эндпоинту phpIPAM: {error_api}")
# GET запрос к phpIPAM на получение Devices
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def get_phpipam_devices(phpipam_api_endpoint):
    try:
        url = f"{PHPIPAM_URL}/{PHPIPAM_APP_ID}/{phpipam_api_endpoint}/" # Формируем URL для запроса данных о секции
        print(f"Обработка запроса по эндпоинту: {url}")
        response = requests.get(url, headers=HEADERS_PHPIPAM, verify=False)

        if response.status_code == 200:
            print("Успешный запрос данных из phpIPAM.")
            return response.json()
        else:
            print(f"Ошибка при запросе данных: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к эндпоинту phpIPAM: {error_api}")

# Функция для получения типа Devices
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def get_phpipam_devices_type(type_id):
    try:
        url = f"{PHPIPAM_URL}/{PHPIPAM_APP_ID}/tools/device_types/{type_id}/" # Формируем URL для запроса данных о типе девайсе
        print(f"Обработка запроса по эндпоинту: {url}")
        response = requests.get(url, headers=HEADERS_PHPIPAM, verify=False)
        if response.status_code == 200:
            print("Успешный запрос данных из phpIPAM.")
            tname = response.json().get("data", []).get("tname")
            tdescription = response.json().get("data", []).get("tdescription")
            return tname, tdescription;
        else:
            print(f"Ошибка при запросе данных: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к эндпоинту phpIPAM: {error_api}")

# Функция для открытия разных json файлов
def load_data_from_json(file_path):
    """Загрузка данных из JSON-файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
        # Декодируем JSON-строку в объект Python
            data = json.loads(data)
            logging.info(f"Данные успешно загружены из {file_path}.")
            return data
    except Exception as e:
        logging.error(f"Ошибка загрузки данных из файла {file_path}: {e}")
        return []
# Генерация ссылок для NetBOX из названий в phpIPAM (русские символы в латиницу)
def clean_slug(name):
    """
    Очищает строку для использования в качестве slug.
    Транслитерирует русские символы в латиницу, удаляет недопустимые символы.
    """
    # Транслитерация русского текста в латиницу
    slug = translit(name, 'ru', reversed=True)
    # Удаляем недопустимые символы
    slug = re.sub(r'[^\w\s-]', '', slug)
    # Заменяем пробелы на подчеркивания и переводим в нижний регистр
    return slug.strip().lower().replace(" ", "_")
# Создание локации из данных phpIPAM в NetBOX
def create_site_in_netbox(location):
    """
    Создает сайт в NetBox на основе информации о локации из phpIPAM.
    """
    if not location:
        return None  # Если информации о локации нет, пропускаем
    slug = clean_slug(location["name"])  # Очистка slug
    site_data = {
        "name": location["name"],
        "slug": slug,
        "description": location.get("description", ""),
        "physical_address": location.get("address", ""),
        "latitude": location.get("lat", None),
        "longitude": location.get("long", None),
    }
    response = requests.post(f"{NETBOX_URL}/dcim/sites/", headers=HEADERS_NETBOX, json=site_data, verify=False)
    if response.status_code == 201:
        print(f"Сайт {site_data['name']} успешно создан в NetBox.")
        return response.json()["id"]  # Возвращаем ID сайта
    elif response.status_code == 400 and "name" in response.json():
        print(f"Сайт {site_data['name']} уже существует.")
        # Если сайт уже существует, получаем его ID
        existing_sites = requests.get(f"{NETBOX_URL}/dcim/sites/?name={site_data['name']}", headers=HEADERS_NETBOX, verify=False)
        if existing_sites.status_code == 200 and existing_sites.json()["count"] > 0:
            return existing_sites.json()["results"][0]["id"]
    else:
        print(f"Ошибка при создании сайта: {response.status_code} - {response.text}")
        return None
# Создание VLANs из данных phpIPAM в NetBOX
def create_vlan_in_netbox(vlan_data):
    # Проверяет существование VLAN в NetBox по VID и возвращает его ID, если найден.
    def get_existing_vlan(vlan_vid):
        response = requests.get(f"{NETBOX_URL}/ipam/vlans/?vid={vlan_vid}", headers=HEADERS_NETBOX, verify=False)
        if response.status_code == 200 and response.json()["count"] > 0:
            return response.json()["results"][0]["id"]
        return None
    """Создание VLAN в NetBox."""
    if not vlan_data:
        return None
    # Проверяем, существует ли VLAN
    existing_vlan_id = get_existing_vlan(int(vlan_data["number"]))
    if existing_vlan_id:
        print(f"VLAN {vlan_data['number']} {vlan_data['name']} уже существует.")
        return existing_vlan_id
    vlan_payload = {
        "name": vlan_data["name"],
        "vid": int(vlan_data["number"]),
        "description": vlan_data.get("description", ""),
    }
    response = requests.post(f"{NETBOX_URL}/ipam/vlans/", headers=HEADERS_NETBOX, json=vlan_payload, verify=False)
    if response.status_code == 201:
        print(f"VLAN {vlan_payload['name']} успешно создан в NetBox.")
        return response.json()["id"]
    elif response.status_code == 400 and "vid" in response.json():
        print(f"VLAN {vlan_payload['vid']} уже существует.")
        # Если VLAN уже существует, получаем его ID
        existing_vlans = requests.get(f"{NETBOX_URL}/ipam/vlans/?vid={vlan_payload['vid']}", headers=HEADERS_NETBOX, verify=False)
        if existing_vlans.status_code == 200 and existing_vlans.json()["count"] > 0:
            return existing_vlans.json()["results"][0]["id"]
    else:
        print(f"Ошибка при создании VLAN: {response.status_code} - {response.text}")
        return None
# Перенос подсетей с локацией и vlan(Обработчик для запросов из phpIPAM в NetBOX) 
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def create_subnets_in_netbox():
    print('Запуск обработчика json - добавление данных: subnets, vlans & locations')
    # Открываем файл и читаем его содержимое
    subnets_data = load_data_from_json('./data/phpipam_data_subnet.json').get("data", [])
    vlans_data = {
        vlan["vlanId"]: vlan 
        for vlan in load_data_from_json('./data/phpipam_data_vlans.json').get("data", [])
    }
    # Определяем диапазон ID
    id_range = (8, 5000)
    total_subnets = len([s for s in subnets_data if id_range[0] <= int(s["id"]) <= id_range[1]])
    bar = IncrementalBar("Обработка подсетей", max=total_subnets)

    processed_count = 0
    for subnet in subnets_data:
        subnet_id = int(subnet["id"])
        if not (id_range[0] <= subnet_id <= id_range[1]):
            continue

        # Создаем сайт на основе информации о локации
        site_id = create_site_in_netbox(subnet.get("location"))
        
        # Проверяем VLAN и создаем его, если связан с подсетью
        vlan_id = subnet.get("vlanId")
        vlan_netbox_id = None
        if vlan_id and vlan_id in vlans_data:
            vlan_netbox_id = create_vlan_in_netbox(vlans_data[vlan_id])

        # Формируем данные для отправки в NetBox
        prefix_data = {
            "prefix": f"{subnet['subnet']}/{subnet['mask']}",
            "description": subnet.get("description", ""),
            "site": site_id,
            "is_pool": bool(int(subnet.get("isPool", 0))),
            "status": "active",  # Устанавливаем статус подсети
            "vlan": vlan_netbox_id,
        }
        # Отправляем данные в NetBox
        response = requests.post(f"{NETBOX_URL}/ipam/prefixes/", headers=HEADERS_NETBOX, json=prefix_data, verify=False)

        if response.status_code == 201:
            print(f"Подсеть {prefix_data['prefix']} успешно создана в NetBox.")
            processed_count += 1
        else:
            print(f"Ошибка при создании подсети {prefix_data['prefix']}: {response.status_code}")
            print(response.text)
        bar.next()
    bar.finish()
    print(f"\nВсего обработано подсетей: {processed_count} из {total_subnets}")

# Перенос IP адрессов(Обработчик для запросов из phpIPAM в NetBOX) 
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def create_addresses_in_netbox():
    print('Запуск обработчика json - добавление данных: ip адреса')
    subnets_data = load_data_from_json('./data/phpipam_data_subnet.json').get("data", [])
    ip_data = load_data_from_json('./data/phpipam_data_addresses.json').get("data", [])

    # Создание словаря для быстрого доступа к маске по subnetId
    subnet_id_to_mask = {
        subnet["id"]: subnet["mask"] for subnet in subnets_data
    }

    # Определяем диапазон ID
    id_range = (8, 20000)
    total_ip = len([s for s in ip_data if id_range[0] <= int(s["id"]) <= id_range[1]])
    bar = IncrementalBar("Обработка IP адресов", max=total_ip)
    processed_count = 0
    for ip in ip_data:
        subnet_id = ip.get("subnetId")
        ip_address = ip.get("ip")
        ip_id = int(ip["id"])
        if not (id_range[0] <= ip_id <= id_range[1]):
            continue
        
        # Получаем маску из данных подсети
        mask = subnet_id_to_mask.get(subnet_id)
        # Формируем адрес в формате ip/mask
        address = f"{ip_address}/{mask}"
        # Очищаем значения hostname от символом которые не принимает Netbox, в netbox нет hostname, вместо него dns name
        dns_name = ip.get("hostname", "") or ""
        dns_name = translit(dns_name, 'ru', reversed=True)
        dns_name = re.sub(r'[^a-zA-Z0-9._*-]', '', dns_name)
        # Формируем данные для отправки в NetBox
        ip_data = {
            "address": address,#ip["ip"]
            "status": "active",
            "description": ip.get("description", "") or "",
            "dns_name": dns_name,
            "comments": ip.get("hostname", "") or "",
        }
        # Отправляем данные в NetBox
        response = requests.post(f"{NETBOX_URL}/ipam/ip-addresses/", headers=HEADERS_NETBOX, json=ip_data, verify=False)
        if response.status_code == 201:
            print(f"IP адрес {ip_data['address']} успешно создан в NetBox.")
            processed_count += 1
        else:
            print(f"Ошибка при создании IP адреса {ip_data['address']}: {response.status_code}")
            print(response.text)
        bar.next()
    bar.finish()
    print(f"\nВсего обработано IP адресов: {processed_count} из {total_ip}")

# Перенос девайсов(Обработчик для запросов из phpIPAM в NetBOX) 
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def create_devices_in_netbox():
    print('Запуск обработчика json - добавление данных: devices')
    locations_data = load_data_from_json('./data/phpipam_data_location.json').get("data", [])
    devices_data = load_data_from_json('./data/phpipam_data_devices.json').get("data", [])

    # Создание словаря для быстрого доступа к локации по id
    location_id_to_address = {
        location["id"]: {
            "name": location.get("name"),
            "description": location.get("description"),
            "address": location.get("address"),
            "lat": location.get("lat"),
            "long": location.get("long"),
        }
        for location in locations_data
    }
    print(location_id_to_address)
    # Определяем диапазон ID
    id_range = (2, 20000)
    total_devices = len([s for s in devices_data if id_range[0] <= int(s["id"]) <= id_range[1]])
    bar = IncrementalBar("Обработка девайсов", max=total_devices)
    processed_count = 0
    for device in devices_data:
        device_id = int(device["id"])
        if not (id_range[0] <= device_id <= id_range[1]):
            continue
        
        id_type = device.get("type")
        device_type = get_phpipam_devices_type(id_type)

        # Очищаем значения hostname от символом которые не принимает Netbox, в netbox нет hostname, вместо него dns name
        dns_name = device.get("hostname", "") or ""
        dns_name = translit(dns_name, 'ru', reversed=True)
        dns_name = re.sub(r'[^a-zA-Z0-9._*-]', '', dns_name)
        # Формируем slug для location
        location_data = location_id_to_address.get(device.get("location"), {})
        
        location_slug = location_data.get("name") or ""
        location_slug = clean_slug(location_slug)
        site_data = {
            "name": location_data.get("name", ""),
            "slug": location_slug,
            "description": location_data.get("description", ""),
            "physical_address": location_data.get("address", ""),
            "latitude": location_data.get("lat", None),
            "longitude": location_data.get("long", None),
        }
        print(site_data)
        
        # Формируем данные для отправки в NetBox
        device_data = {
            "name": dns_name,
            "device_type": {
                "manufacturer": {
                "name": device.get("custom_Vendor", "") or "",
                "slug": clean_slug(device.get("custom_Vendor", "")) or "",
                "description": "",
                },
                "model": device.get("custom_Model", "") or "",
                "slug": clean_slug(device.get("custom_Model")) or "",
                "description": "",
            },
            "role": {
                "name": f"{device_type[0]}",
                "slug": clean_slug(device_type[0]),
                "description": f"{device_type[1]}",
            },
            "platform": {
                "name": device.get("custom_Firmware", "") or "",
                "slug": clean_slug(device.get("custom_Firmware")) or "",
                "description": ""
            },
            "serial": device.get("custom_Serial", "") or "",
            "site": {
                "name": site_data.get("name"),
                "slug": site_data.get("slug"),
                "description": site_data.get("description"),
            },
            "latitude": site_data.get("latitude"),
            "longitude": site_data.get("longitude"),
            "status": "active",
            "primary_ip4": {
                "address": device.get("ip", "") or "",
                "description": ""
            },
            "description": device.get("description", "") or "",
            "comments": device.get("description", "") or "",
        }
        print(device_data)
        # Отправляем данные в NetBox
        response = requests.post(f"{NETBOX_URL}/dcim/devices/", headers=HEADERS_NETBOX, json=device_data, verify=False)
        if response.status_code == 201:
            print(f"Устройство {device_data['name']} успешно создано в NetBox.")
            processed_count += 1
        else:
            print(f"Ошибка при создании устройства {device_data['name']}: {response.status_code}")
            print(response.text)
        bar.next()
    bar.finish()
    print(f"\nВсего обработано устройств: {processed_count} из {total_devices}")

def generate_location_json():
    """
    Генерирует JSON-файл с данными о локациях из JSON-файла с подсетями.
    """
    output_file_path = "./data/phpipam_data_location.json"
    with open("./data/phpipam_data_subnet.json", "r", encoding="utf-8") as file:
        subnets = json.load(file).get("data", [])

    unique_locations = {}
    for subnet in subnets:
        location = subnet.get("location")
        if location:
            location_id = location["id"]
            if location_id not in unique_locations:
                unique_locations[location_id] = location

    # Формируем данные для записи
    locations_data = {"data": list(unique_locations.values())}
    return locations_data

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
    #create_subnets_in_netbox()
    #create_addresses_in_netbox()
    create_devices_in_netbox()

main_function()

print(f"Исполнение скрипта заняло: {datetime.now() - start_time}")
print("_____________________________________________________________________________________________________________________")