import os
import sqlite3
import urllib.parse

def rename_folder_files(folder_path):
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            new_filename = filename.lower()
            new_full_path = os.path.join(folder_path, new_filename)
            if filename != new_filename:
                try:
                    os.rename(full_path, new_full_path)
                    print(f"Renombrado: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"Error renombrando {filename}: {e}")

def get_image_filename_for_creature(folder_path, creature_name):
    creature_name = creature_name.lower().strip()
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)
        if os.path.isfile(full_path):
            base, ext = os.path.splitext(filename)
            if base == creature_name:
                return filename
    return None

def update_img_urls_for_category(db_path, table_name, category_folder, github_base_url):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT id, name, image_url FROM {table_name}")
    rows = cursor.fetchall()

    for record_id, creature_name, current_url in rows:
        image_filename = get_image_filename_for_creature(category_folder, creature_name)
        if image_filename:
            encoded_filename = urllib.parse.quote(image_filename)  # Esto convierte espacios en %20, etc.
            new_url = f"{github_base_url}{encoded_filename}"
            cursor.execute(f"UPDATE {table_name} SET image_url = ? WHERE id = ?", (new_url, record_id))
            print(f"Actualizado {creature_name}: {new_url}")
        else:
            print(f"No se encontró imagen para '{creature_name}' en {category_folder}")

    conn.commit()
    conn.close()

def main():
    bosses_folder = os.path.join("assets", "bosses")
    monsters_folder = os.path.join("assets", "monsters")

    print("Renombrando archivos en la carpeta bosses...")
    rename_folder_files(bosses_folder)
    print("Renombrando archivos en la carpeta monsters...")
    rename_folder_files(monsters_folder)

    db_path = os.path.join("data", "bontar_data.db")

    github_base_bosses = "https://raw.githubusercontent.com/Andreesb/alystarpedia-data/main/assets/bosses/"
    github_base_monsters = "https://raw.githubusercontent.com/Andreesb/alystarpedia-data/main/assets/monsters/"

    print("\nActualizando imagenes en la tabla 'bosses'...")
    update_img_urls_for_category(db_path, "bosses", bosses_folder, github_base_bosses)

    print("\nActualizando imagenes en la tabla 'monsters'...")
    update_img_urls_for_category(db_path, "monsters", monsters_folder, github_base_monsters)

    print("\nProceso completado.")

if __name__ == "__main__":
    main()
