import os
import sqlite3
import urllib.parse
import sys

# --------------------------
# Función para renombrar archivos a minúsculas
# --------------------------
def rename_folder_files(folder_path):
    """
    Renombra todos los archivos en folder_path para que sus nombres sean minúsculas.
    """
    for filename in os.listdir(folder_path):
        # Construir rutas completas
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            new_filename = filename.lower()
            new_full_path = os.path.join(folder_path, new_filename)
            # Si el nombre actual no está en minúsculas, renombrarlo
            if filename != new_filename:
                try:
                    os.rename(full_path, new_full_path)
                    print(f"Renombrado: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"Error renombrando {filename}: {e}")

# --------------------------
# Función para buscar el archivo de imagen que coincide con un nombre (sin extensión)
# dentro de una carpeta determinada.
# --------------------------
def get_image_filename_for_creature(folder_path, creature_name):
    """
    Busca en folder_path un archivo cuyo nombre (sin extensión) coincida con creature_name.
    La comparación se hace en minúsculas.
    Retorna el nombre completo (con extensión) si se encuentra, o None en caso contrario.
    """
    creature_name = creature_name.lower().strip()
    for filename in os.listdir(folder_path):
        # Considera solo archivos
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            # Separamos el nombre base y la extensión
            base, ext = os.path.splitext(filename)
            # Comparar el base (en minúsculas) con el creature_name
            if base == creature_name:
                return filename  # Retorna el nombre completo (por ejemplo: "a shielded astral glyph.gif")
    return None

# --------------------------
# Función para actualizar la columna img_url en la base de datos.
# --------------------------
def update_img_urls_for_category(db_path, table_name, category_folder, github_base_url):
    """
    Busca en la tabla de la base de datos (bosses o monsters) cada registro y, utilizando el campo 'name'
    (convertido a minúsculas), intenta localizar en la carpeta category_folder el archivo correspondiente.
    Si lo encuentra, actualiza la columna 'img_url' con la URL basada en github_base_url.
    
    Parameters:
       - db_path: ruta a la base de datos (por ejemplo "data/bontar_data.db").
       - table_name: nombre de la tabla ("bosses" o "monsters").
       - category_folder: ruta a la carpeta local (por ejemplo "assets/bosses").
       - github_base_url: base URL del repositorio, p.ej.
         "https://raw.githubusercontent.com/Andreesb/alystarpedia-data/refs/heads/main/assets/bosses/"
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Seleccionar todos los registros
    cursor.execute(f"SELECT id, name, image_url FROM {table_name}")
    rows = cursor.fetchall()
    
    for row in rows:
        record_id, creature_name, current_url = row
        # Buscar el archivo en la carpeta; se espera que la imagen ya se haya renombrado a minúsculas.
        image_filename = get_image_filename_for_creature(category_folder, creature_name)
        if image_filename:
            # URL encode el nombre del archivo para espacios y caracteres especiales
            encoded_filename = urllib.parse.quote(image_filename)
            new_url = f"{github_base_url}{encoded_filename}"
            cursor.execute(f"UPDATE {table_name} SET image_url = ? WHERE id = ?", (new_url, record_id))
            print(f"Actualizado {creature_name}: {new_url}")
        else:
            print(f"No se encontró imagen para '{creature_name}' en {category_folder}")
    
    conn.commit()
    conn.close()

# --------------------------
# Parámetros y ejecución
# --------------------------
def main():
    # Rutas locales de las carpetas en assets
    bosses_folder = os.path.join("assets", "bosses")
    monsters_folder = os.path.join("assets", "monsters")
    
    # Renombrar archivos en ambas carpetas a minúsculas
    print("Renombrando archivos en la carpeta bosses...")
    rename_folder_files(bosses_folder)
    print("Renombrando archivos en la carpeta monsters...")
    rename_folder_files(monsters_folder)
    
    # Ruta de la base de datos
    db_path = os.path.join("data", "bontar_data.db")
    
    # Base URL para el repositorio en GitHub
    github_base_bosses = "https://raw.githubusercontent.com/Andreesb/alystarpedia-data/refs/heads/main/assets/bosses/"
    github_base_monsters = "https://raw.githubusercontent.com/Andreesb/alystarpedia-data/refs/heads/main/assets/monsters/"
    
    # Actualizar la tabla bosses
    print("\nActualizando imagenes en la tabla 'bosses'...")
    update_img_urls_for_category(db_path, "bosses", bosses_folder, github_base_bosses)
    
    # Actualizar la tabla monsters
    print("\nActualizando imagenes en la tabla 'monsters'...")
    update_img_urls_for_category(db_path, "monsters", monsters_folder, github_base_monsters)
    
    print("\nProceso completado.")

if __name__ == "__main__":
    main()
