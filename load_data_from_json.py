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