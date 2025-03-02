import requests
import re
import json


# Proxy (ajústalo según el servicio que uses)
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

all_urls= set()

for i in range(65):
    # URL de Fotocasa
    url = f"https://www.fotocasa.es/es/alquiler/viviendas/valencia-capital/todas-las-zonas/l/{i+1}"
    # Hacer la petición usando el proxy
    response = requests.get(url, headers=headers, proxies=proxies)
    # Verificar si la petición fue exitosa
    if response.status_code == 200:
        script_text = response.text  # Tratar el HTML como texto plano
        matches = re.findall(r'\/es\/alquiler\/vivienda\/valencia-capital\/[^\s"\']+', script_text)
        
        print(f"🔹 Se encontraron {len(matches)} enlaces:")
        for match in matches:
            all_urls.add(match)
        print("guardado")
    else:
        print(f"❌ Error {response.status_code}: No se pudo acceder a la página")

# Guardar en un archivo JSON
with open("all_urls.json", "w", encoding="utf-8") as f:
    json.dump(list(all_urls), f, ensure_ascii=False, indent=4)