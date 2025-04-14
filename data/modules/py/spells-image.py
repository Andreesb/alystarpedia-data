import os
import json
import requests

def download_spell_images(json_file, output_folder):
    """
    Abre el archivo JSON con los datos de los spells, extrae la URL de la imagen de cada spell
    y la descarga en la carpeta especificada.
    
    Args:
        json_file (str): Ruta del archivo JSON (por ejemplo, "Spells.json").
        output_folder (str): Carpeta donde se guardarán las imágenes.
    """
    
    # Crear la carpeta de destino si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Abrir y cargar los datos del JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        spells = json.load(f)
    
    for spell in spells:
        image_url = spell.get("image_url", "")
        if image_url and image_url != "no image":
            try:
                response = requests.get(image_url)
                if response.status_code == 200:
                    # Se intenta obtener la extensión de la imagen a partir de la URL
                    _, ext = os.path.splitext(image_url)
                    if not ext:
                        ext = ".gif"  # Valor por defecto si no se encuentra extensión
                    # Generar nombre del archivo basado en el nombre del spell
                    # Se elimina espacios y se utiliza minúsculas
                    spell_name = spell.get("name", "unknown").strip().lower().replace(" ", "_")
                    filename = f"{spell_name}{ext}"
                    filepath = os.path.join(output_folder, filename)
                    with open(filepath, "wb") as img_file:
                        img_file.write(response.content)
                    print(f"Descargada imagen: {filepath}")
                else:
                    print(f"Error al descargar imagen para '{spell.get('name')}' - Código: {response.status_code}")
            except Exception as e:
                print(f"Excepción al descargar imagen para '{spell.get('name')}'. URL: {image_url}. Detalle: {e}")
        else:
            print(f"Sin imagen para '{spell.get('name')}'.")
            

# Ejemplo de uso:
if __name__ == "__main__":
    json_file = "Spells.json"
    output_folder = "assets/spells"
    download_spell_images(json_file, output_folder)
