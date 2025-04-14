import os
import json
import sqlite3

def load_json(filepath):
    """Carga y devuelve el contenido del JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def build_spawn_mapping(bosses_by_tag_path, arena_bosses_path):
    """
    Construye un diccionario que mapea (en minúsculas) cada nombre de boss a una lista de spawn types,
    combinando los datos de bosses_by_tag.json y arena_bosses.json.
    """
    spawn_mapping = {}

    # Cargar bosses_by_tag.json
    bosses_by_tag = load_json(bosses_by_tag_path)
    for stype, bosses in bosses_by_tag.items():
        for boss in bosses:
            key = boss.lower().strip()
            if key in spawn_mapping:
                if stype not in spawn_mapping[key]:
                    spawn_mapping[key].append(stype)
            else:
                spawn_mapping[key] = [stype]

    # Cargar arena_bosses.json
    arena_bosses = load_json(arena_bosses_path)
    for entry in arena_bosses:
        boss_name = entry.get("name", "").lower().strip()
        types = entry.get("spawn_type", [])
        if boss_name:
            if boss_name in spawn_mapping:
                for stype in types:
                    if stype not in spawn_mapping[boss_name]:
                        spawn_mapping[boss_name].append(stype)
            else:
                spawn_mapping[boss_name] = types

    return spawn_mapping

def update_bosses_spawn_type(db_path, spawn_mapping):
    """
    Conecta a la base de datos y actualiza la columna 'spawn_type' en la tabla 'bosses'
    según el mapping proporcionado. Si el boss no se encuentra en el mapping, verifica si
    la columna 'notes' contiene la palabra 'minion' para asignar 'minion' como spawn_type;
    de lo contrario, asigna 'special'.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Seleccionar todos los jefes de la tabla
    cursor.execute("SELECT id, name, notes FROM bosses")
    rows = cursor.fetchall()

    for record_id, name, notes in rows:
        key = name.lower().strip()
        if key in spawn_mapping:
            spawn_types = spawn_mapping[key]
            new_spawn = ", ".join(spawn_types)
        else:
            if notes and "minion" in notes.lower():
                new_spawn = "minion"
            else:
                new_spawn = "special"
        cursor.execute("UPDATE bosses SET spawn_type = ? WHERE id = ?", (new_spawn, record_id))
        print(f"Actualizado '{name}': {new_spawn}")

    conn.commit()
    conn.close()
    print("Actualización completada.")

def main():
    # Rutas de los archivos JSON
    bosses_by_tag_path = os.path.join("bosses_by_tag.json")
    arena_bosses_path = os.path.join("arena_bosses.json")
    db_path = os.path.join("data", "bontar_data.db")

    # Construir el mapeo de spawn types
    spawn_mapping = build_spawn_mapping(bosses_by_tag_path, arena_bosses_path)
    print("Mapa de spawn types construido:")
    for boss, types in spawn_mapping.items():
        print(f"{boss}: {types}")

    # Actualizar la base de datos de bosses según el mapping
    update_bosses_spawn_type(db_path, spawn_mapping)

if __name__ == "__main__":
    main()
