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