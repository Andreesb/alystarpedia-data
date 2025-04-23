import sqlite3
import os
from PIL import Image, ImageSequence

# Configuración de rutas y URLs
DB_PATH = 'data/bontar_data.db'
MONSTER_STATIC_DIR = 'assets/monsters-estaticos'
BOSS_STATIC_DIR = 'assets/bosses-estaticos'
MONSTER_GIF_DIR = 'assets/monsters'
BOSS_GIF_DIR = 'assets/bosses'
BASE_URL_MONSTER = 'https://raw.githubusercontent.com/andreesb/alystarpedia-data/main/assets/monsters-estaticos/'
BASE_URL_BOSS    = 'https://raw.githubusercontent.com/andreesb/alystarpedia-data/main/assets/bosses-estaticos/'

def add_column_if_not_exists(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    if 'static_img' not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN static_img TEXT")
        conn.commit()

def list_files(dir_path):
    try:
        return set(os.listdir(dir_path))
    except FileNotFoundError:
        return set()

def match_static_filename(name, filenames):
    """
    Empareja 'lion' con 'lions.png', etc.
    """
    base = name.lower().replace(' ', '')
    for form in (base, base + 's'):
        for ext in ('.png', '.jpg', '.gif'):
            fname = form + ext
            if fname in filenames:
                return fname
    return None

def process_table(conn, table, static_dir, base_url):
    add_column_if_not_exists(conn, table)
    static_files = list_files(static_dir)
    cur = conn.cursor()
    cur.execute(f"SELECT id, name FROM {table}")
    missing = []
    for id_, name in cur.fetchall():
        fname = match_static_filename(name, static_files)
        if fname:
            url = base_url + fname
            cur.execute(f"UPDATE {table} SET static_img = ? WHERE id = ?", (url, id_))
        else:
            missing.append((id_, name))
    conn.commit()
    return missing

def match_gif_filename(name, filenames):
    """
    Empareja 'the count of the core' con 'the count of the core.gif', insensible a mayúsculas.
    """
    target = name.lower()
    for fname in filenames:
        base, ext = os.path.splitext(fname)
        if ext.lower() == '.gif' and base.lower() == target:
            return fname
    return None

def extract_static_from_gif(gif_path, save_path):
    with Image.open(gif_path) as img:
        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
        n = len(frames)
        idx = 1 if n == 2 else n // 2
        frames[idx].save(save_path)

def process_missing(missing, gif_dir, static_dir, base_url, conn, table):
    gif_files = list_files(gif_dir)
    for id_, name in missing:
        gif_fname = match_gif_filename(name, gif_files)
        if not gif_fname:
            print(f"[!] GIF no encontrado para '{name}'")
            continue

        gif_path = os.path.join(gif_dir, gif_fname)
        save_fname = os.path.splitext(gif_fname)[0] + '.gif'
        save_path = os.path.join(static_dir, save_fname)
        os.makedirs(static_dir, exist_ok=True)

        try:
            extract_static_from_gif(gif_path, save_path)
            url = base_url + save_fname
            conn.execute(f"UPDATE {table} SET static_img = ? WHERE id = ?", (url, id_))
        except Exception as e:
            print(f"[!] Error extrayendo frame de '{gif_path}': {e}")

def main():
    conn = sqlite3.connect(DB_PATH)

    # Procesar monsters
    missing_monsters = process_table(conn, 'monsters',
                                     MONSTER_STATIC_DIR, BASE_URL_MONSTER)
    process_missing(missing_monsters, MONSTER_GIF_DIR,
                    MONSTER_STATIC_DIR, BASE_URL_MONSTER,
                    conn, 'monsters')

    # Procesar bosses
    missing_bosses = process_table(conn, 'bosses',
                                   BOSS_STATIC_DIR, BASE_URL_BOSS)
    process_missing(missing_bosses, BOSS_GIF_DIR,
                    BOSS_STATIC_DIR, BASE_URL_BOSS,
                    conn, 'bosses')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
