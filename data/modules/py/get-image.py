import os
import sqlite3
import requests
from urllib.parse import urlparse, unquote

# Archivo de la base de datos
DB_FILE = 'data/bontar_data.db'
BOSSES_DIR = 'bosses'
MONSTERS_DIR = 'monsters'

os.makedirs(BOSSES_DIR, exist_ok=True)
os.makedirs(MONSTERS_DIR, exist_ok=True)

# Lista de alternativas para URL que fallan (creatures_failed)
creature_failed = [
    {
        "name": "dragon pack",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Despor.gif"
    },
    {
        "name": "dragon wardens",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Dragon%20Warden.gif"
    },
    {
        "name": "lagatoses",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Lagatos.gif"
    },
    {
        "name": "man in the cave",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Man%20in%20the%20Cave.gif"
    },
    {
        "name": "draptors",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Draptor.gif"
    },
    {
        "name": "midnight panthers",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Midnight%20Panther.gif"
    },
    {
        "name": "piñata dragons",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Piñata%20Dragon.gif"
    },
    {
        "name": "crustaceae giganticae",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Crustacea%20Gigantica.gif"
    },
    {
        "name": "yalaharis",
        "image_url": "https://tibia.fandom.com/wiki/Special:Redirect/file/Azerus.gif"  # Según tu ejemplo
    },
]

def get_filename_from_url(url):
    """
    Extrae y decodifica el nombre del archivo desde una URL.
    Si la URL es completa (comienza con "http"), se extrae el basename
    de la ruta y se eliminan parámetros de consulta.
    """
    if url.startswith("http"):
        parsed = urlparse(url)
        filename = os.path.basename(unquote(parsed.path))
        if '?' in filename:
            filename = filename.split('?')[0]
        return filename if filename else "image.gif"
    else:
        path = urlparse(url).path
        filename = os.path.basename(unquote(path))
        return filename if filename else "image.gif"

def try_alternative_url(url):
    """
    Dado el URL original, intenta encontrar una URL alternativa en creature_failed
    comparando el nombre base (sin extensión) en minúsculas.
    """
    filename = get_filename_from_url(url)  # Ej: "dragon pack.gif"
    base_name = os.path.splitext(filename)[0].lower().strip()  # Ej: "dragon pack"
    
    for entry in creature_failed:
        alt_name = entry["name"].lower().strip()
        # Se puede usar una comparación exacta o incluir alguna lógica de coincidencia parcial
        if base_name == alt_name:
            return entry["image_url"]
    return None

def download_image(url, save_path):
    """
    Descarga la imagen desde la URL y la guarda en save_path.
    Retorna True si la descarga fue exitosa, False en caso contrario.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)
        print(f"Descargada: {url} -> {save_path}")
        return True
    except Exception as e:
        print(f"Error al descargar {url}: {e}")
        return False

def download_images_from_table(cursor, table_name, folder, fail_list):
    """
    Descarga las imágenes de la columna image_url de la tabla indicada y las guarda
    en la carpeta especificada. Si falla la descarga, intenta con la URL alternativa.
    Si ésta también falla, agrega la URL original a fail_list.
    """
    query = f"SELECT image_url FROM {table_name}"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        url = row[0]
        if not url:
            continue
        
        # Procesa la URL (ya actualizada en la base de datos)
        filename = get_filename_from_url(url)
        save_path = os.path.join(folder, filename)
        
        # Si el archivo ya existe, saltar descarga.
        if os.path.exists(save_path):
            print(f"El archivo {save_path} ya existe; saltando descarga.")
            continue
        
        # Intentar descargar desde la URL original.
        if download_image(url, save_path):
            continue
        else:
            # Intentar la URL alternativa.
            alt_url = try_alternative_url(url)
            if alt_url:
                print(f"Intentando URL alternativa: {alt_url}")
                if download_image(alt_url, save_path):
                    continue
            # Si también falla, se agrega a la lista de fallos.
            fail_list.append(url)

def main():
    failed_bosses = []
    failed_monsters = []
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("Descargando imágenes de bosses...")
    download_images_from_table(cursor, "bosses", BOSSES_DIR, failed_bosses)
    
    print("Descargando imágenes de monsters...")
    download_images_from_table(cursor, "monsters", MONSTERS_DIR, failed_monsters)
    
    conn.close()
    
    if failed_bosses:
        print("Las siguientes imágenes de bosses no se pudieron descargar:")
        for url in failed_bosses:
            print(url)
    else:
        print("Todas las imágenes de bosses se descargaron correctamente.")
    
    if failed_monsters:
        print("Las siguientes imágenes de monsters no se pudieron descargar:")
        for url in failed_monsters:
            print(url)
    else:
        print("Todas las imágenes de monsters se descargaron correctamente.")

if __name__ == "__main__":
    main()
