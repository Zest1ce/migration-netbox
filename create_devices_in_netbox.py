@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException, 
                       JSONDecodeError), 
                       max_tries=5)
def create_devices_in_netbox():
    print('Запуск обработчика json - добавление данных: devices')
    locations_data = load_data_from_json('./data/phpipam_data_location.json').get("data", [])
    devices_data = load_data_from_json('./data/phpipam_data_devices.json').get("data", [])

    # Создание словаря для быстрого доступа к локации по id
    location_id_to_address = {
        location["id"]: {
            "name": location.get("name"),
            "description": location.get("description"),
            "address": location.get("address"),
            "lat": location.get("lat"),
            "long": location.get("long"),
        }
        for location in locations_data
    }
    print(location_id_to_address)
    # Определяем диапазон ID
    id_range = (2, 20000)
    total_devices = len([s for s in devices_data if id_range[0] <= int(s["id"]) <= id_range[1]])
    bar = IncrementalBar("Обработка девайсов", max=total_devices)
    processed_count = 0
    for device in devices_data:
        device_id = int(device["id"])
        if not (id_range[0] <= device_id <= id_range[1]):
            continue
        
        id_type = device.get("type")
        device_type = get_phpipam_devices_type(id_type)

        # Очищаем значения hostname от символом которые не принимает Netbox, в netbox нет hostname, вместо него dns name
        dns_name = device.get("hostname", "") or ""
        dns_name = translit(dns_name, 'ru', reversed=True)
        dns_name = re.sub(r'[^a-zA-Z0-9._*-]', '', dns_name)
        # Формируем slug для location
        location_data = location_id_to_address.get(device.get("location"), {})
        
        location_slug = location_data.get("name") or ""
        location_slug = clean_slug(location_slug)
        site_data = {
            "name": location_data.get("name", ""),
            "slug": location_slug,
            "description": location_data.get("description", ""),
            "physical_address": location_data.get("address", ""),
            "latitude": location_data.get("lat", None),
            "longitude": location_data.get("long", None),
        }
        print(site_data)
        
        # Формируем данные для отправки в NetBox
        device_data = {
            "name": dns_name,
            "device_type": {
                "manufacturer": {
                "name": device.get("custom_Vendor", "") or "",
                "slug": clean_slug(device.get("custom_Vendor", "")) or "",
                "description": "",
                },
                "model": device.get("custom_Model", "") or "",
                "slug": clean_slug(device.get("custom_Model")) or "",
                "description": "",
            },
            "role": {
                "name": f"{device_type[0]}",
                "slug": clean_slug(device_type[0]),
                "description": f"{device_type[1]}",
            },
            "platform": {
                "name": device.get("custom_Firmware", "") or "",
                "slug": clean_slug(device.get("custom_Firmware")) or "",
                "description": ""
            },
            "serial": device.get("custom_Serial", "") or "",
            "site": {
                "name": site_data.get("name"),
                "slug": site_data.get("slug"),
                "description": site_data.get("description"),
            },
            "latitude": site_data.get("latitude"),
            "longitude": site_data.get("longitude"),
            "status": "active",
            "primary_ip4": {
                "address": device.get("ip", "") or "",
                "description": ""
            },
            "description": device.get("description", "") or "",
            "comments": device.get("description", "") or "",
        }
        print(device_data)
        # Отправляем данные в NetBox
        response = requests.post(f"{NETBOX_URL}/dcim/devices/", headers=HEADERS_NETBOX, json=device_data, verify=False)
        if response.status_code == 201:
            print(f"Устройство {device_data['name']} успешно создано в NetBox.")
            processed_count += 1
        else:
            print(f"Ошибка при создании устройства {device_data['name']}: {response.status_code}")
            print(response.text)
        bar.next()
    bar.finish()
    print(f"\nВсего обработано устройств: {processed_count} из {total_devices}")