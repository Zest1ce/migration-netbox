# Перенос IP адрессов(Обработчик для запросов из phpIPAM в NetBOX) 
@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def create_addresses_in_netbox():
    print('Запуск обработчика json - добавление данных: ip адреса')
    subnets_data = load_data_from_json('./data/phpipam_data_subnet.json').get("data", [])
    ip_data = load_data_from_json('./data/phpipam_data_addresses.json').get("data", [])

    # Создание словаря для быстрого доступа к маске по subnetId
    subnet_id_to_mask = {
        subnet["id"]: subnet["mask"] for subnet in subnets_data
    }

    # Определяем диапазон ID
    id_range = (8, 20000)
    total_ip = len([s for s in ip_data if id_range[0] <= int(s["id"]) <= id_range[1]])
    bar = IncrementalBar("Обработка IP адресов", max=total_ip)
    processed_count = 0
    for ip in ip_data:
        subnet_id = ip.get("subnetId")
        ip_address = ip.get("ip")
        ip_id = int(ip["id"])
        if not (id_range[0] <= ip_id <= id_range[1]):
            continue
        
        # Получаем маску из данных подсети
        mask = subnet_id_to_mask.get(subnet_id)
        # Формируем адрес в формате ip/mask
        address = f"{ip_address}/{mask}"
        # Очищаем значения hostname от символом которые не принимает Netbox, в netbox нет hostname, вместо него dns name
        dns_name = ip.get("hostname", "") or ""
        dns_name = translit(dns_name, 'ru', reversed=True)
        dns_name = re.sub(r'[^a-zA-Z0-9._*-]', '', dns_name)
        # Формируем данные для отправки в NetBox
        ip_data = {
            "address": address,#ip["ip"]
            "status": "active",
            "description": ip.get("description", "") or "",
            "dns_name": dns_name,
            "comments": ip.get("hostname", "") or "",
        }
        # Отправляем данные в NetBox
        response = requests.post(f"{NETBOX_URL}/ipam/ip-addresses/", headers=HEADERS_NETBOX, json=ip_data, verify=False)
        if response.status_code == 201:
            print(f"IP адрес {ip_data['address']} успешно создан в NetBox.")
            processed_count += 1
        else:
            print(f"Ошибка при создании IP адреса {ip_data['address']}: {response.status_code}")
            print(response.text)
        bar.next()
    bar.finish()
    print(f"\nВсего обработано IP адресов: {processed_count} из {total_ip}")