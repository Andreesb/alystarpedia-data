import os
import json
import requests

# Ruta al archivo JSON (puedes ajustarlo si es otro nombre o formato)
json_file = "imbuements.json"
output_folder = "imbuements"

# Crear carpeta si no existe
os.makedirs(output_folder, exist_ok=True)

# Cargar JSON
with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Función para descargar una imagen desde una URL
def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Imagen guardada: {save_path}")
        else:
            print(f"Error al descargar {url}: código {response.status_code}")
    except Exception as e:
        print(f"Error al descargar {url}: {e}")

# Procesar todos los niveles de cada categoría
for category in data:
    levels = category.get("levels", {})
    for tier in levels.values():
        for imbuement in tier:
            name = imbuement.get("name", "unknown").lower()  # minúsculas sin reemplazar espacios
            image_url = imbuement.get("image_url")

            # Obtener extensión del archivo (por defecto .gif)
            extension = os.path.splitext(image_url.split("?")[0])[1] or ".gif"

            save_path = os.path.join(output_folder, f"{name}{extension}")
            if image_url:
                download_image(image_url, save_path)
