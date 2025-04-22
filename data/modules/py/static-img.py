import os
import re
import requests
from urllib.parse import urlparse

# -------------------------------------------------------------------
# Configuración de endpoints y carpetas de salida
# -------------------------------------------------------------------
BOSS_URL     = 'https://api.tibiadata.com/v4/boostablebosses'
CREATURE_URL = 'https://api.tibiadata.com/v4/creatures'

BOSS_FOLDER     = 'bosses-estaticos'
CREATURE_FOLDER = 'monsters-estaticos'

# -------------------------------------------------------------------
# Helper para crear carpetas
# -------------------------------------------------------------------
def ensure_folder(path):
    os.makedirs(path, exist_ok=True)

# -------------------------------------------------------------------
# Helper para limpiar nombre de fichero (solo usa el nombre)
# -------------------------------------------------------------------
def safe_filename(name, ext=''):
    # Reemplaza espacios y caracteres no permitidos
    base = re.sub(r'[^\w\-_\. ]', '_', name).strip()
    return f"{base}{ext}"

# -------------------------------------------------------------------
# Descarga una lista de items JSON con key 'image_url'
# -------------------------------------------------------------------
def download_images(items, folder):
    ensure_folder(folder)
    for entry in items:
        name    = entry.get('name') or 'unknown'
        img_url = entry.get('image_url')
        if not img_url:
            print(f"[SKIP] {name}: no image_url")
            continue

        # Calcular extensión
        parsed = urlparse(img_url)
        m = re.search(r'\.(jpg|jpeg|png|gif)(?:$|\?)', parsed.path, re.IGNORECASE)
        ext = f".{m.group(1).lower()}" if m else ''

        # Nombre de fichero limpio
        fname = safe_filename(name, ext)
        fpath = os.path.join(folder, fname)

        # Descargar
        try:
            print(f"Downloading {name} → {fname}")
            r = requests.get(img_url, timeout=10)
            r.raise_for_status()
            with open(fpath, 'wb') as f:
                f.write(r.content)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")

# -------------------------------------------------------------------
# Proceso para Boostable Bosses
# -------------------------------------------------------------------
def fetch_and_save_boss_images():
    resp = requests.get(BOSS_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    boss_block = data.get('boostable_bosses', {})
    boss_list  = boss_block.get('boostable_boss_list', [])
    boosted    = boss_block.get('boosted')
    if boosted:
        boss_list.insert(0, boosted)

    download_images(boss_list, BOSS_FOLDER)

# -------------------------------------------------------------------
# Proceso para Creatures
# -------------------------------------------------------------------
def fetch_and_save_creature_images():
    resp = requests.get(CREATURE_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    creatures_block = data.get('creatures', {})
    creature_list   = creatures_block.get('creature_list', [])
    boosted         = creatures_block.get('boosted')
    if boosted:
        creature_list.insert(0, boosted)

    download_images(creature_list, CREATURE_FOLDER)

# -------------------------------------------------------------------
# Ejecución principal
# -------------------------------------------------------------------
if __name__ == '__main__':
    print("=== Downloading Boss Images ===")
    fetch_and_save_boss_images()
    print("\n=== Downloading Creature Images ===")
    fetch_and_save_creature_images()
    print("\nDone!")
