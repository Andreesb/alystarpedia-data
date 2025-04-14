import json
import os
import sqlite3





def actualizar_image_urls(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        spells = json.load(file)

    for spell in spells:
        nombre = spell.get("name", "").strip().lower().replace(" ", "_")
        spell["image_url"] = f"https://raw.githubusercontent.com/Andreesb/alystarpedia-data/main/assets/spells/{nombre}.gif"

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(spells, file, indent=4, ensure_ascii=False)


def crear_tabla_y_agregar_datos(json_path, db_path):
    # Conectar a la base de datos (o crearla si no existe)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear la tabla 'spells'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            name TEXT,
            image_url TEXT,
            words TEXT,
            mana TEXT,
            subclass TEXT,
            cooldown TEXT,
            voc TEXT,
            premium BOOLEAN,
            promotion BOOLEAN,
            level_required TEXT,
            cost TEXT,
            learn_from TEXT,
            city TEXT,
            implemented TEXT,
            status TEXT
        )
    ''')

    # Leer los datos del archivo JSON
    with open(json_path, 'r', encoding='utf-8') as file:
        spells = json.load(file)

    # Insertar cada hechizo en la tabla
    for spell in spells:
        attributes = spell.get("attributes", {})
        # Obtener el valor de voc y procesarlo
        voc_raw = attributes.get("voc", "")
        voc_list = [v.strip() for v in voc_raw.split()] if voc_raw else []
        voc_str = ", ".join(voc_list)  # Convertimos la lista a string con comas

        # Obtener learn_from info
        learn_info = spell.get("learn_from", [{}])
        if isinstance(learn_info, list) and len(learn_info) > 0:
            npc = learn_info[0].get("npc")
            city = learn_info[0].get("city")
        else:
            npc = None
            city = None

        cursor.execute('''
            INSERT INTO spells (
                url, name, image_url, words, mana, subclass, cooldown, voc,
                premium, promotion, level_required, cost, learn_from, city,
                implemented, status
                
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            spell.get("url"),
            spell.get("name"),
            spell.get("image_url"),
            attributes.get("words"),
            attributes.get("mana"),
            attributes.get("subclass"),
            attributes.get("cooldown"),
            voc_str,  # Ahora separado por coma
            attributes.get("premium"),
            attributes.get("promotion"),
            attributes.get("level_required"),
            attributes.get("cost"),
            npc,
            city,
            attributes.get("implemented"),
            attributes.get("status")
        ))



    # Confirmar los cambios y cerrar la conexión
    conn.commit()
    conn.close()



# Ruta al archivo JSON
ruta_json = 'data/Spells.json'

# Ruta a la base de datos SQLite
ruta_db = 'data/bontar_data.db'

# Actualizar las URLs de las imágenes
actualizar_image_urls(ruta_json)

# Crear la tabla y agregar los datos
crear_tabla_y_agregar_datos(ruta_json, ruta_db)
