import os
import sqlite3
import re

def clean_bosses_db(db_path='data/bontar_data.db'):
    """
    Abre la base de datos SQLite, procesa la tabla 'bosses' para:
    1. Eliminar comas dentro de números en paréntesis (ej. "1,000" -> "1000").
    2. Remover el nombre de la criatura (columna 'name') de la cadena de 'abilities'.
    3. Normalizar espacios y comas.
    4. Convertir la columna 'category' a Title Case.
    """
    if not os.path.exists(db_path):
        print(f"Base de datos no encontrada: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, abilities, category FROM bosses")
    rows = cursor.fetchall()

    updated = 0
    for row in rows:
        id_, name, abilities, category = row
        if not abilities:
            continue

        # Función para eliminar comas entre dígitos dentro de paréntesis
        def remove_commas(match):
            text = match.group(0)
            return re.sub(r'(?<=\d),(?=\d)', '', text)

        # 1. Quitar comas en números dentro de paréntesis
        new_abilities = re.sub(r'\([^)]*\)', remove_commas, abilities)

        # 2. Eliminar el nombre de la criatura, coincidencia exacta (case-insensitive)
        new_abilities = re.sub(fr'\b{re.escape(name)}\b', '', new_abilities, flags=re.IGNORECASE)

        # 3. Normalizar comas y espacios
        new_abilities = re.sub(r'\s*,\s*', ', ', new_abilities).strip(', ').strip()

        # 4. Title case para category
        new_category = category.title() if category else category

        # Actualizar solo si hubo cambios
        if new_abilities != abilities or new_category != category:
            cursor.execute(
                "UPDATE bosses SET abilities = ?, category = ? WHERE id = ?",
                (new_abilities, new_category, id_)
            )
            updated += 1

    conn.commit()
    conn.close()
    print(f"Filas actualizadas: {updated}")

# Ejecutar limpieza
clean_bosses_db()
