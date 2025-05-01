import os
import json
from urllib.parse import quote

# Carpeta donde están las imágenes
IMAGES_DIR = "assets/key-collector"
# Ruta al JSON
JSON_PATH = "Keys.json"
# Base URL para raw.githubusercontent
RAW_BASE = "https://raw.githubusercontent.com/andreesb/alystarpedia-data/refs/heads/main/assets/key-collector/"

def rename_images_and_update_json(images_dir=IMAGES_DIR, json_path=JSON_PATH):
    # Renombrar imágenes
    for filename in os.listdir(images_dir):
        old_path = os.path.join(images_dir, filename)
        if os.path.isfile(old_path):
            name, ext = os.path.splitext(filename)
            new_name = name.lower().replace('_', ' ') + ext.lower()
            new_path = os.path.join(images_dir, new_name)
            os.rename(old_path, new_path)
            print(f"Renombrado: {filename} → {new_name}")

    # Cargar JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Actualizar image_url en cada entrada
    for item in data:
        # Extraer nombre de archivo de la ruta antigua
        old_url = item.get("image_url", "")
        basename = os.path.basename(old_url)
        name, ext = os.path.splitext(basename)
        new_filename = name.lower().replace('_', ' ') + ext.lower()
        # Construir URL raw
        encoded_name = quote(new_filename)
        new_url = RAW_BASE + encoded_name
        item["image_url"] = new_url
        print(f"Actualizado JSON: {basename} → {new_url}")

    # Guardar cambios en JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("JSON actualizado correctamente.")

if __name__ == "__main__":
    rename_images_and_update_json()
