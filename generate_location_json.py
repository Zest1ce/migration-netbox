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