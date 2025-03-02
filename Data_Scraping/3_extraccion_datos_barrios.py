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

with open("all_ZoneSlug.json", "r", encoding="utf-8") as f:
    urls = json.load(f)


all_data= []


for i in urls:
    url = f"https://www.fotocasa.es/es/vivir-en-valencia-capital/{i}"
    try:
        this_zone_data = {"URL": url, "zoneSlug": i}

        response = requests.get(url, headers=headers, proxies=proxies)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            try:
                valoracion_estrellas = float(soup.select_one("strong.re-GeoGeneralRating-valRatings").text.replace(",","."))
            except:
                valoracion_estrellas = None
            this_zone_data["GeoGeneralRating"] = valoracion_estrellas
            # Contacto anunciante
            script_tag = soup.find("script", id="sui-scripts")
            script_text = script_tag.string
            # Expresión regular para extraer JSON dentro de JSON.parse(...)
            # match = re.search(r'window\.__INITIAL_PROPS__\s*=\s*JSON\.parse\((.*?)\);', script_text)
            match = re.search(r'window\.__INITIAL_PROPS__\s*=\s*JSON\.parse\([\'"](.+?)[\'"]\);', script_text)
            json_str = match.group(1)
            json_str = json_str.encode().decode("unicode_escape")  # Desescapamos caracteres
            # print(json_str)
            # Decodificar el JSON escapado dentro del JSON.parse
            try:
                data = json.loads(json_str)
                # print(data["realEstateAdDetailEntityV2"]["publisher"].keys())
                for i in data["geoAdvisor"]["transactions"]:
                    tipo = i["type"]
                    propertyCounter = i["propertyCounter"]
                    priceDescription = int(i["priceDescription"].replace("€","").replace(".","").strip())
                    this_zone_data[f"propertyCounter_{tipo}"]=propertyCounter
                    this_zone_data[f"priceDescription_{tipo}"]=priceDescription
                metro_count = data["geoServices"]["services"]["transport"]["counts"]["metro"]
                tram_count = data["geoServices"]["services"]["transport"]["counts"]["tram"]
                train_count = data["geoServices"]["services"]["transport"]["counts"]["train"]
                supermarket_count = data["geoServices"]["services"]["feeding"]["counts"]["supermarket"]
                pharmacy_count = data["geoServices"]["services"]["health"]["counts"]["pharmacy"]
                hospital_count = data["geoServices"]["services"]["health"]["counts"]["hospital"]
                university_count = data["geoServices"]["services"]["training"]["counts"]["university"]
                college_count = data["geoServices"]["services"]["training"]["counts"]["college"]

                this_zone_data["metro_count"] = metro_count
                this_zone_data["tram_count"] = tram_count
                this_zone_data["train_count"] = train_count
                this_zone_data["supermarket_count"] = supermarket_count
                this_zone_data["pharmacy_count"] = pharmacy_count
                this_zone_data["hospital_count"] = hospital_count
                this_zone_data["university_count"] = university_count
                this_zone_data["college_count"] = college_count

            except Exception as e:
                print(f"Error al decodificar el JSON. {e}")

        else:
            print(f"❌ {url} - Error {response.status_code}")

    except requests.exceptions.RequestException as e:                        
        print(f"⚠️ Error con {url}: {e}")

    all_data.append(this_zone_data)
    with open("zoneInformation.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)