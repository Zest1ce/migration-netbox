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