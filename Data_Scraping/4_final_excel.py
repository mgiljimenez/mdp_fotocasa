import json
import pandas as pd

# Cargar los archivos JSON
with open("zoneInformation.json", "r", encoding="utf-8") as f:
    zoneinfo = json.load(f)  # Lista de diccionarios

with open("property_data.json", "r", encoding="utf-8") as f:
    property_data = json.load(f)  # Lista de diccionarios

# Convertir a DataFrames
df_properties = pd.DataFrame(property_data)  # Propiedades
df_zones = pd.DataFrame(zoneinfo)  # Información de zonas

# Unir por 'zoneSlug'
df_final = df_properties.merge(df_zones, on="zoneSlug", how="left")
df_final.to_excel("fotocasa.xlsx", index=False, engine="openpyxl")
