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