import sqlite3
import json

# Ruta al archivo JSON con las categorías de los jefes
json_path = "bosses_by_tag.json"

# Cargar el archivo JSON
with open(json_path, "r", encoding="utf-8") as f:
    bosses_by_tag = json.load(f)

# Conectar con la base de datos
conn = sqlite3.connect("data/bontar_data.db")
cursor = conn.cursor()

# Agregar la columna 'spawn_type' si no existe
try:
    cursor.execute("ALTER TABLE bosses ADD COLUMN spawn_type TEXT")
    conn.commit()
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("La columna 'spawn_type' ya existe.")
    else:
        raise

# Crear un diccionario con el nombre del boss en minúscula y su categoría
boss_to_spawn_type = {}
for spawn_type, boss_list in bosses_by_tag.items():
    for boss in boss_list:
        boss_to_spawn_type[boss.lower()] = spawn_type

# Asignar la categoría correspondiente a cada boss en la tabla
cursor.execute("SELECT name FROM bosses")
all_bosses = cursor.fetchall()

for (boss_name,) in all_bosses:
    spawn_type = boss_to_spawn_type.get(boss_name.lower(), "special")
    cursor.execute("""
        UPDATE bosses
        SET spawn_type = ?
        WHERE LOWER(name) = ?
    """, (spawn_type, boss_name.lower()))

conn.commit()

# Verificar los jefes que quedaron con categoría 'special'
cursor.execute("SELECT name FROM bosses WHERE spawn_type = 'special'")
special_bosses = [row[0] for row in cursor.fetchall()]

conn.close()

# Mostrar resultados
print("Columna 'spawn_type' agregada y actualizada correctamente.")
print("\nJefes con spawn_type 'special':")
for boss in special_bosses:
    print("-", boss)
