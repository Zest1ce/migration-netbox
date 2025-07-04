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

# Вызов функции load_data_from_json
from load_data_from_json import load_data_from_json
# Вызов функции create_site_in_netbox
from create_site_in_netbox import create_site_in_netbox
# Вызов функции create_vlan_in_netbox
from create_vlan_in_netbox import create_vlan_in_netbox
# Получение кредов
from credential import PHPIPAM_URL, PHPIPAM_APP_ID, PHPIPAM_API_TOKEN, NETBOX_URL, NETBOX_API_TOKEN
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