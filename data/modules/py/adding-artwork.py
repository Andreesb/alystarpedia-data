import os
import sqlite3

# Ruta a la carpeta de imágenes
ART_DIR = 'assets/artworks/creatures'
# Base de la URL donde se alojan los artworks
URL_BASE = 'https://raw.githubusercontent.com/andreesb/alystarpedia-data/main/assets/artworks/creatures'

# 1) Renombrar archivos: lowercase + '_' → ' '
def normalize_filenames(directory):
    for fname in os.listdir(directory):
        # sólo JPEGs
        if not fname.lower().endswith('.jpg'):
            continue
        src = os.path.join(directory, fname)
        # Nuevo nombre: minusculas, guiones bajos a espacios
        name_only, ext = os.path.splitext(fname)
        new_name_only = name_only.lower().replace('_', ' ')
        new_fname = f"{new_name_only}{ext.lower()}"
        dst = os.path.join(directory, new_fname)
        if src != dst:
            os.rename(src, dst)
            print(f"Renamed: '{src}' → '{dst}'")

# 2) Actualizar la DB
def update_monster_artwork(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Añadir columna artwork si no existe
    cur.execute("""
      PRAGMA table_info(monsters)
    """)
    cols = [info[1] for info in cur.fetchall()]
    if 'artwork' not in cols:
        cur.execute("ALTER TABLE monsters ADD COLUMN artwork TEXT")
        print("Added 'artwork' column to monsters")

    # Leer todos los monsters
    cur.execute("SELECT id, name FROM monsters")
    rows = cur.fetchall()
    for mid, name in rows:
        # Construir slug igual que el nombre de archivo
        slug = name.lower().replace(' ', ' ')
        # Asegúrate de escapar caracteres especiales si los hay
        url = f"{URL_BASE}/{slug}.jpg"
        # Actualizar fila
        cur.execute(
            "UPDATE monsters SET artwork = ? WHERE id = ?",
            (url, mid)
        )
    conn.commit()
    conn.close()
    print("Updated artwork URLs in database")

if __name__ == '__main__':
    normalize_filenames(ART_DIR)
    update_monster_artwork('data/bontar_data.db')
