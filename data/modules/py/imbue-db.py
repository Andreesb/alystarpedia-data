import os
import json
import sqlite3

# Rutas
json_path = os.path.join("imbuements.json")
db_path = "data/bontar_data.db"

# Conectar a SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tabla de imbuements
cursor.execute('''
CREATE TABLE IF NOT EXISTS imbuements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    level TEXT,
    percentage TEXT,
    image_url TEXT,
    category TEXT,
    astral_sources TEXT,
    available_for TEXT
)
''')
conn.commit()

# Cargar JSON
with open(json_path, "r", encoding="utf-8") as f:
    imbuements = json.load(f)

# Insertar datos
inserted_count = 0
for imbue in imbuements:
    category = imbue.get("imbuement_category")
    levels = imbue.get("levels", {})

    for level_name, entries in levels.items():
        for entry in entries:
            name = entry.get("name").lower()
            percentage = entry.get("percentage")
            image_url = f"https://raw.githubusercontent.com/andreesb/alystarpedia-data/main/assets/imbuements/{name}.gif"

            # Convertir listas a JSON string
            astral_sources = json.dumps(entry.get("astral_sources", []), ensure_ascii=False)
            available_for = json.dumps(entry.get("available_for", []), ensure_ascii=False)

            cursor.execute('''
                INSERT OR REPLACE INTO imbuements (
                    name, level, percentage, image_url, category, astral_sources, available_for
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                name, level_name.capitalize(), percentage, image_url, category, astral_sources, available_for
            ))
            inserted_count += 1

conn.commit()
conn.close()
print(f"{inserted_count} imbuements insertados/actualizados.")
