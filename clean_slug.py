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