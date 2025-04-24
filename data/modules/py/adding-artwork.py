import sqlite3
import os
import re

def update_monster_artwork(db_path: str, artwork_dir: str, base_url: str):
    """
    Opens the SQLite database at db_path, ensures the 'artwork' column exists
    in the 'monsters' table, and updates each monster with a URL to its artwork
    if a corresponding file exists in artwork_dir. Otherwise, leaves the artwork
    field as NULL.
    
    Matching logic:
    - Normalize monster names and filenames to lowercase, remove non-alphanumerics.
    - Strip version suffixes (like ' v8.00') from filenames.
    - Match when normalized filename starts with normalized monster name.
    """
    def normalize(text: str) -> str:
        # Lowercase, remove accents, non-alphanumeric, collapse whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
        return re.sub(r'\s+', '_', text.strip())

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure artwork column exists
    cursor.execute("PRAGMA table_info(monsters)")
    cols = [c[1] for c in cursor.fetchall()]
    if 'artwork' not in cols:
        cursor.execute("ALTER TABLE monsters ADD COLUMN artwork TEXT")

    # Prepare filename map: normalized base -> actual filename
    files = [f for f in os.listdir(artwork_dir) if os.path.isfile(os.path.join(artwork_dir, f))]
    file_map = {}
    for f in files:
        base, ext = os.path.splitext(f)
        # Remove trailing version info: anything after ' v\d'
        base_clean = re.sub(r'\s+v\d.*$', '', base, flags=re.IGNORECASE)
        norm = normalize(base_clean)
        file_map[norm] = f

    # Update each monster
    cursor.execute("SELECT id, name FROM monsters")
    for mid, name in cursor.fetchall():
        key = normalize(name)
        # find matching file by prefix
        filename = None
        if key in file_map:
            filename = file_map[key]
        else:
            # try partial match
            for norm_file, f in file_map.items():
                if norm_file.startswith(key):
                    filename = f
                    break
        artwork_url = f"{base_url}{filename}" if filename else None
        cursor.execute("UPDATE monsters SET artwork = ? WHERE id = ?", (artwork_url, mid))

    conn.commit()
    conn.close()

# Example usage
update_monster_artwork(
    db_path="data/bontar_data.db",
    artwork_dir="assets/artworks/creatures",
    base_url="https://raw.githubusercontent.com/andreesb/alystarpedia-data/main/assets/artworks/creatures/"
)
