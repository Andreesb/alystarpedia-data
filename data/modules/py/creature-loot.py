import json
import sqlite3

# Cargar datos del JSON
with open("loot_data.json", "r", encoding="utf-8") as f:
    creature_loot = json.load(f)

# Conectar a la base de datos
conn = sqlite3.connect("data/bontar_data.db")
cursor = conn.cursor()

# Convertir nombres a minúscula para coincidencia flexible
loot_map = {name.lower(): loot for name, loot in creature_loot.items()}

# Obtener nombres de bosses
cursor.execute("SELECT name FROM bosses")
boss_names = [row[0].lower() for row in cursor.fetchall()]

# Actualizar bosses
for name in boss_names:
    if name in loot_map:
        loot_text = ", ".join(loot_map[name]).lower()
        cursor.execute("UPDATE bosses SET loot = ? WHERE LOWER(name) = ?", (loot_text, name))

# Obtener nombres de monsters
cursor.execute("SELECT name FROM monsters")
monster_names = [row[0] for row in cursor.fetchall()]

for name in monster_names:
    lname = name.lower()
    if lname in boss_names:
        # Si ya existe en bosses, eliminarlo de monsters
        cursor.execute("DELETE FROM monsters WHERE LOWER(name) = ?", (lname,))
    elif lname in loot_map:
        loot_text = ", ".join(loot_map[lname]).lower()
        cursor.execute("UPDATE monsters SET loot = ? WHERE LOWER(name) = ?", (loot_text, lname))

# Guardar y cerrar
conn.commit()
conn.close()
print("Loot actualizado y duplicados eliminados.")
