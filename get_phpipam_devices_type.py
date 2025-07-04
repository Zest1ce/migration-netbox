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