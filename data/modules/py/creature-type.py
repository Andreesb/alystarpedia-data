import requests
from bs4 import BeautifulSoup
import json

# URL de la página de Arena Bosses en Tibia Fandom
url = "https://tibia.fandom.com/wiki/Arena_Bosses"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

arena_data = []

# Buscar todos los encabezados <h2> que tengan un <span class="mw-headline"> y contengan "Arena Bosses"
headers = soup.find_all("h2")
tables = []
for header in headers:
    span = header.find("span", class_="mw-headline")
    if span and "Arena Bosses" in span.text:
        # Extraer el nombre de la arena quitando "Arena Bosses"
        arena_name_full = span.text.strip()
        arena_name = arena_name_full.replace("Arena Bosses", "").strip()
        # Buscar el siguiente elemento <table> con clase "wikitable"
        table = header.find_next_sibling("table", class_="wikitable")
        if table:
            tables.append((arena_name, table))

# Procesar las tablas extraídas
# Se asume que:
#   - Las tres primeras tablas corresponden a arenas normales, con spawn_type "arena"
#   - La última tabla corresponde a arenas de quest, con spawn_type "arena quest"
results = []
total_tables = len(tables)
for idx, (arena_name, table) in enumerate(tables):
    spawn_type = "arena" if idx < total_tables - 1 else "arena quest"
    # Extraer las criaturas: buscamos enlaces <a> que sean hijos del table.
    # Para evitar enlaces no deseados, comprobamos que el href comience con "/wiki/".
    links = table.find_all("a", href=True)
    for link in links:
        href = link.get("href")
        if href.startswith("/wiki/"):
            creature_name = link.text.strip()
            if creature_name:
                results.append({
                    "name": creature_name,
                    "spawn_type": [arena_name.lower(), spawn_type]
                })

# Guardar los resultados en un archivo JSON
with open("arena_bosses.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Extracción completada. Los datos se han guardado en 'arena_bosses.json'.")
