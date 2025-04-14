import os
import json
import sqlite3

# 1. Definir la carpeta donde se encuentran los archivos JSON y la ruta de la base de datos
json_folder = os.path.join("data", "equipament")
db_path = "data/bontar_data.db"

# 2. Conectarse a la base de datos SQLite y crear la tabla "equipaments"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    name TEXT,
    image_url TEXT,
    notes TEXT,
    dropped_by TEXT,
    level TEXT,
    vocation TEXT,
    imbuing_slots TEXT,
    upgrade_classification TEXT,
    extra_attributes TEXT,
    armor TEXT,
    resists TEXT,
    classification TEXT,
    pickupable BOOLEAN,
    weight TEXT,
    stackable BOOLEAN,
    marketable BOOLEAN,
    value TEXT,
    sold_for BOOLEAN,
    bought_for BOOLEAN,
    blocking BOOLEAN,
    version TEXT,
    category TEXT
)
''')
conn.commit()

# 3. Función para cargar un JSON desde un archivo
def load_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# 4. Recorrer cada archivo JSON en la carpeta
for filename in os.listdir(json_folder):
    if filename.lower().endswith(".json"):
        filepath = os.path.join(json_folder, filename)
        # Usar el nombre del archivo (sin extensión) como categoría
        category = os.path.splitext(filename)[0].lower()
        try:
            items = load_json_file(filepath)
        except Exception as e:
            print(f"Error cargando {filename}: {e}")
            continue

        # 5. Recorrer cada item dentro del archivo JSON
        for item in items:
            url = item.get("url")
            # Convertir el nombre a minúsculas
            name = item.get("name", "").lower()
            image_url = item.get("image_url")
            notes = item.get("notes")
            # Convertir la lista 'dropped_by' a una cadena separada por comas
            dropped_by_list = item.get("dropped_by", [])
            dropped_by = ", ".join(dropped_by_list) if isinstance(dropped_by_list, list) else dropped_by_list

            # Extraer atributos desde el diccionario "attributes"
            attrs = item.get("attributes", {})
            level = attrs.get("Level")
            vocation = attrs.get("Vocation")
            imbuing_slots = attrs.get("Imbuing Slots")
            upgrade_classification = attrs.get("Upgrade Classification")
            extra_attributes = attrs.get("Attributes")
            armor = attrs.get("Armor")
            resists = attrs.get("Resists")
            classification = attrs.get("Classification")
            pickupable = attrs.get("Pickupable")
            weight = attrs.get("Weight")
            stackable = attrs.get("Stackable")
            marketable = attrs.get("Marketable")
            value = attrs.get("Value")
            sold_for = attrs.get("Sold for")
            bought_for = attrs.get("Bought for")
            blocking = attrs.get("Blocking")
            version = attrs.get("Version")

            # 6. Insertar los datos en la tabla "equipaments"
            cursor.execute('''
            INSERT INTO items (
                url, name, image_url, notes, dropped_by,
                level, vocation, imbuing_slots, upgrade_classification,
                extra_attributes, armor, resists, classification, pickupable,
                weight, stackable, marketable, value, sold_for, bought_for, blocking, version, category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (url, name, image_url, notes, dropped_by,
                  level, vocation, imbuing_slots, upgrade_classification,
                  extra_attributes, armor, resists, classification, pickupable,
                  weight, stackable, marketable, value, sold_for, bought_for, blocking, version, category))
        conn.commit()
        print(f"Datos del archivo {filename} agregados a la base de datos bajo la categoría '{category}'.")

conn.close()
print("Todos los datos han sido insertados correctamente en la tabla items.")
