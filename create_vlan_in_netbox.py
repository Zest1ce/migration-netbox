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