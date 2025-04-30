import sqlite3
import re

def split_abilities(text: str) -> list[str]:
    """
    Divide la cadena text por comas al nivel 0 de paréntesis,
    conservando cualquier '.' final en cada segmento.
    """
    result = []
    buf = ''
    depth = 0
    for ch in text:
        if ch == '(':
            depth += 1
            buf += ch
        elif ch == ')':
            depth = max(0, depth - 1)
            buf += ch
        elif depth == 0 and ch == ',':
            result.append(buf.strip())
            buf = ''
        else:
            buf += ch
    if buf.strip():
        result.append(buf.strip())
    return result

def clean_monster_abilities(db_path: str):
    """
    Abre el SQLite en db_path, lee monsters.name y monsters.abilities,
    limpia las habilidades que incluyan el nombre (fuera de paréntesis)
    y actualiza la columna abilities.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, abilities FROM monsters")
    rows = cursor.fetchall()

    for mid, name, abilities in rows:
        if not abilities:
            continue

        lower_name = name.lower()
        segments = split_abilities(abilities)
        cleaned = []

        for seg in segments:
            seg_lower = seg.lower()
            # Si contiene el nombre de la criatura
            # y NO está dentro de paréntesis, la descartamos
            if lower_name in seg_lower and not ('(' in seg and ')' in seg):
                continue
            cleaned.append(seg)

        new_abilities = ', '.join(cleaned)

        cursor.execute(
            "UPDATE monsters SET abilities = ? WHERE id = ?",
            (new_abilities, mid)
        )

    conn.commit()
    conn.close()

# Uso:
if __name__ == '__main__':
    clean_monster_abilities('data/bontar_data.db')
