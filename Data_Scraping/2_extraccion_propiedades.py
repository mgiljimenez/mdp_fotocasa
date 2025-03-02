import requests
import re
import json
from bs4 import BeautifulSoup

proxy = ""

# Headers para evitar bloqueos
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Configurar el proxy en requests
proxies = {
    "http": proxy,
    "https": proxy
}

with open("all_urls.json", "r", encoding="utf-8") as f:
    urls = json.load(f)


output_file = "property_data.json"
error_file = "error.json"
all_data = []
error_data = []


def find_key(data, target_key, path=""):
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            if key == target_key:
                return new_path  # Retorna la ruta a la clave encontrada
            found = find_key(value, target_key, new_path)
            if found:
                return found
    elif isinstance(data, list):
        for index, item in enumerate(data):
            new_path = f"{path}[{index}]"
            found = find_key(item, target_key, new_path)
            if found:
                return found
    return None  # No encontrado


for url in urls:
    try:
        this_property_data = {"URL": "https://www.fotocasa.es" + url.rstrip('\\')}
        full_url = "https://www.fotocasa.es" + url.rstrip('\\')

        response = requests.get(full_url, headers=headers, proxies=proxies)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Extraer Título
            try:
                property_title = soup.select_one("h1.re-DetailHeader-propertyTitle").text
                this_property_data["propertyTitle"] = property_title
            except:
                this_property_data["propertyTitle"] = None
            # Contacto anunciante
            script_tag = soup.find("script", id="sui-scripts")
            script_text = script_tag.string
            # Expresión regular para extraer JSON dentro de JSON.parse(...)
            match = re.search(r'window\.__INITIAL_PROPS__\s*=\s*JSON\.parse\((.*?)\);', script_text)
            json_str = match.group(1)
            # Decodificar el JSON escapado dentro del JSON.parse
            try:
                data = json.loads(json.loads(json_str))
                # print(data["realEstateAdDetailEntityV2"]["publisher"].keys())
                latitud = data["realEstateAdDetailEntityV2"]["address"]["coordinates"]["lat"]
                this_property_data["lat"] = latitud

                longitud = data["realEstateAdDetailEntityV2"]["address"]["coordinates"]["lng"]
                this_property_data["lng"] = longitud

                municipio = data["realEstateAdDetailEntityV2"]["address"]["municipality"]
                this_property_data["municipality"] = municipio

                barrio = data["realEstateAdDetailEntityV2"]["address"]["neighborhood"]
                this_property_data["neighborhood"] = barrio

                this_property_data["zoneSlug"] = data["realEstate"]["relatedGeoInfo"]["zoneSlug"]

                codigo_postal = data["realEstateAdDetailEntityV2"]["address"]["zipCode"]
                this_property_data["zipCode"] = codigo_postal
                

                duenio_tipo = data["realEstateAdDetailEntityV2"]["publisher"]["type"]
                this_property_data["ownerType"] = duenio_tipo

                duenio_id = data["realEstateAdDetailEntityV2"]["id"]
                this_property_data["ownerId"] = duenio_id


                fecha_creacion = data["realEstateAdDetailEntityV2"]["creationDate"]
                this_property_data["creationDate"] = fecha_creacion

                this_property_data["energyEfficiencyRatingType"] = data.get("realEstateAdDetailEntityV2", {}).get("energyCertificate", {}).get("energyEfficiencyRatingType", None)

                this_property_data["energyEfficiency"] = data.get("realEstateAdDetailEntityV2", {}).get("energyCertificate", {}).get("energyEfficiency", None)

                this_property_data["environmentImpact"] = data.get("realEstateAdDetailEntityV2", {}).get("energyCertificate", {}).get("environmentImpact", None)

                this_property_data["environmentImpactRatingType"] = data.get("realEstateAdDetailEntityV2", {}).get("energyCertificate", {}).get("environmentImpactRatingType", None)


                tipo_construccion = data["realEstateAdDetailEntityV2"]["constructionType"]
                this_property_data["constructionType"] = tipo_construccion

                # features_extra = data["realEstateAdDetailEntityV2"]["extraFeatures"]
                tiene_online_tour = data["realEstateAdDetailEntityV2"]["hasOnlineGuidedTour"]
                this_property_data["hasOnlineGuidedTour"] = tiene_online_tour

                for feature in data["realEstateAdDetailEntityV2"]["features"]:
                    this_property_data[feature] = data["realEstateAdDetailEntityV2"]["features"][feature]

                price = data["realEstateAdDetailEntityV2"]["price"]["amount"]
                this_property_data["priceAmount"] = price

                price_drop = data["realEstateAdDetailEntityV2"]["price"]["amountDrop"]
                this_property_data["priceAmountDrop"] = price_drop

                ascensor = "Ascensor" in data["realEstateAdDetailEntityV2"]["extraFeatures"]
                this_property_data["tieneAscensor"] = ascensor

                trastero = "Trastero" in data["realEstateAdDetailEntityV2"]["extraFeatures"]
                this_property_data["tieneTrastero"] = trastero

                calefaccion = "Calefacción" in data["realEstateAdDetailEntityV2"]["extraFeatures"]
                this_property_data["tieneCalefaccion"] = calefaccion

                aire_acondicionado = "Aire acondicionado" in data["realEstateAdDetailEntityV2"]["extraFeatures"]
                this_property_data["tieneAireAcondicionado"] = aire_acondicionado

                propertyTypeId = data["realEstateAdDetailEntityV2"]["propertyTypeId"]
                this_property_data["propertyTypeId"] = propertyTypeId

                propertySubtypeId = data["realEstateAdDetailEntityV2"]["propertySubtypeId"]
                this_property_data["propertySubtypeId"] = propertySubtypeId
            except:
                print("Error al decodificar el JSON.")

        else:
            print(f"❌ {full_url} - Error {response.status_code}")

    except requests.exceptions.RequestException as e:                        
        print(f"⚠️ Error con {full_url}: {e}")

    all_data.append(this_property_data)
    with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
