# GET запрос к phpIPAM на получение подсетей
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def get_phpipam_subnets(phpipam_api_endpoint):
    try:
        url = f"{PHPIPAM_URL}/{PHPIPAM_APP_ID}/{phpipam_api_endpoint}/" # Формируем URL для запроса данных о секции
        print(f"Обработка запроса по эндпоинту: {url}")
        response = requests.get(url, headers=HEADERS_PHPIPAM, verify=False)

        if response.status_code == 200:
            print("Успешный запрос данных из phpIPAM.")
            return response.json()
        else:
            print(f"Ошибка при запросе данных: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as error_api:
        print(f"Произошла ошибка при подключении к эндпоинту phpIPAM: {error_api}")