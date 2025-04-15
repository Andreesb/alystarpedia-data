import sqlite3

def categorize_monsters(db_path="bontar_data.db"):
    """
    Consulta la base de datos y obtiene los nombres de las criaturas de la tabla 'monsters'. 
    Luego las categoriza en tres listas basándose en si su nombre contiene (case insensitive)
    la palabra "quest", "raid" o "event".
    
    Args:
        db_path (str): Ruta de la base de datos SQLite.
        
    Returns:
        tuple: Cuatro listas (quests, raids, events, others) con los nombres de los monsters categorizados.
    """
    # Conexión a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ejecutar consulta para obtener el nombre de las criaturas
    cursor.execute("SELECT name FROM monsters")
    rows = cursor.fetchall()
    conn.close()
    
    # Extraer los nombres de las filas
    monsters = [row[0] for row in rows]
    
    # Inicializar listas para cada categoría
    quest_monsters = []
    raid_monsters = []
    event_monsters = []
    others = []
    
    # Categorizar usando condiciones sobre el nombre (todo en minúsculas)
    for name in monsters:
        name_lower = name.lower()
        if "quest" in name_lower:
            quest_monsters.append(name)
        elif "raid" in name_lower:
            raid_monsters.append(name)
        elif "event" in name_lower:
            event_monsters.append(name)
        else:
            others.append(name)
    
    return quest_monsters, raid_monsters, event_monsters, others

if __name__ == "__main__":
    # Ajusta la ruta de la base de datos si es necesario
    db_path = "data/bontar_data.db"
    quests, raids, events, others = categorize_monsters(db_path)
    
    print("Monstruos de quests:")
    for m in quests:
        print(" -", m)
    print("\nMonstruos de raids:")
    for m in raids:
        print(" -", m)
    print("\nMonstruos de event:")
    for m in events:
        print(" -", m)
    print("\nOtros monstruos:")
    for m in others:
        print(" -", m)
