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