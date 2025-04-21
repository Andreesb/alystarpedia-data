import sqlite3
import re

def clean_abilities(abilities: str, creature_name: str) -> str:
    """
    - Elimina comas dentro de números (ej. "1,000" -> "1000").
    - Borra menciones del nombre de la criatura a menos que vengan precedidas de "minion of".
    - Limpia espacios y comas redundantes.
    """
    # 1) Eliminar comas entre dígitos
    abilities = re.sub(r'(?<=\d),(?=\d)', '', abilities)
    
    # 2) Eliminar nombre de criatura no precedido por "minion of"
    pattern = re.compile(
        rf'(?<!minion of )\b{re.escape(creature_name)}\b',
        flags=re.IGNORECASE
    )
    abilities = pattern.sub('', abilities)
    
    # 3) Limpiar espacios múltiples y comas duplicadas
    abilities = re.sub(r'\s{2,}', ' ', abilities)
    abilities = re.sub(r',\s*,', ',', abilities)
    abilities = abilities.strip(' ,')
    
    return abilities

def process_table(conn: sqlite3.Connection, table: str):
    cur = conn.cursor()
    cur.execute(f"SELECT id, name, abilities FROM {table}")
    rows = cur.fetchall()
    
    for id_, name, abilities in rows:
        if not abilities:
            continue
        cleaned = clean_abilities(abilities, name)
        if cleaned != abilities:
            cur.execute(
                f"UPDATE {table} SET abilities = ? WHERE id = ?",
                (cleaned, id_)
            )
    conn.commit()

def main():
    db_path = 'data/bontar_data.db'
    conn = sqlite3.connect(db_path)
    
    for table in ['bosses', 'monsters']:
        process_table(conn, table)
    
    conn.close()

if __name__ == "__main__":
    main()

