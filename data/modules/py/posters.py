import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3
import json  # Importamos el módulo json

# ================================
# 1. Conexión a la base de datos y extracción de nombres
# ================================
def obtener_nombres_criaturas(db_path="data/bontar_data.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM bosses")
    boss_names = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT name FROM monsters")
    monster_names = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    creature_names = list(set(boss_names + monster_names))
    return creature_names

# ================================
# 2. Normalización de nombres y creación de variantes
# ================================
def generar_variantes(nombre):
    nombre_lower = nombre.lower().strip()
    variante_guion = nombre_lower.replace(" ", "_")
    variante_percent = nombre_lower.replace(" ", "%20")
    return {nombre_lower, variante_guion, variante_percent}

creature_names = obtener_nombres_criaturas()
variantes_criaturas = {}
for nombre in creature_names:
    variantes_criaturas[nombre.lower()] = generar_variantes(nombre)

# ================================
# 3. Configuración del scraping
# ================================
base_url = "https://www.tibia.com/news/?subtopic=newsarchive&id="
start_id = 1
end_id = 8353

poster_list = []
onclick_pattern = re.compile(r"window\.open\('([^']+)'")
img_filename_pattern = re.compile(r"/([^/]+)\.(jpg|png)", re.IGNORECASE)

contador = 0

# ================================
# 4. Proceso de scraping y comparación con variantes
# ================================
for post_id in range(start_id, end_id + 1):
    contador += 1
    url = f"{base_url}{post_id}"
    print(f"Procesando ID {post_id} ({contador} de {end_id})")
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"ID {post_id}: Error {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        content_container = soup.find(class_="BoxContent")
        if not content_container:
            continue

        imgs = content_container.find_all("img")
        poster_data = None
        
        for img in imgs:
            onclick_attr = img.get("onclick", "")
            if "window.open(" in onclick_attr:
                match = onclick_pattern.search(onclick_attr)
                if match:
                    large_image_url = match.group(1)
                    small_image_url = img.get("src", "")
                    
                    filename_match = img_filename_pattern.search(small_image_url)
                    nombre_extraido = None
                    if filename_match:
                        nombre_extraido = filename_match.group(1).lower()
                    
                    nombre_detectado = None

                    if nombre_extraido:
                        for nombre_base, variantes in variantes_criaturas.items():
                            if any(variant in nombre_extraido for variant in variantes) or any(variant in large_image_url.lower() for variant in variantes):
                                nombre_detectado = nombre_base
                                break
                   
                    related_link = None
                    if nombre_detectado:
                        links = content_container.find_all("a")
                        for a in links:
                            href = a.get("href", "").lower()
                            if nombre_detectado in href and "news" in href:
                                related_link = href
                                break

                    poster_data = {
                        "page_url": url,
                        "small_image": small_image_url,
                        "large_image": large_image_url,
                        "nombre_extraido": nombre_extraido,
                        "nombre_detectado": nombre_detectado,
                        "related_link": related_link
                    }
                    poster_list.append(poster_data)
                    break
    
    except Exception as e:
        print(f"ID {post_id}: Error {e}")
    
    time.sleep(0.5)

# ================================
# 5. Guardar resultados en archivo JSON
# ================================
output_file = "posters.json"
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(poster_list, f, ensure_ascii=False, indent=4)
    print(f"Se han guardado {len(poster_list)} posters en el archivo '{output_file}'.")
except Exception as e:
    print(f"Error al guardar los datos en '{output_file}': {e}")
