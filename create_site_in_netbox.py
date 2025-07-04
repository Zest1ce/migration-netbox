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

# Вызов функции clean_slug
from clean_slug import clean_slug
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