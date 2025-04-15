import sqlite3

def update_all_text_to_lowercase(db_path="data/bontar_data.db"):
    """
    Actualiza el contenido de todas las columnas con tipo de texto (por ejemplo, TEXT o CHAR)
    de todas las tablas de la base de datos a minúsculas, excepto:
        - La columna 'image_url' en las tablas 'items' y 'equipaments'
        - La columna 'account_status' en cualquier tabla (u otra columna con restricciones críticas)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Consultar nombres de tablas (excluyendo las internas)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    
    # Definir columnas que NO queremos actualizar, independientemente de la tabla
    columnas_excluidas = {"account_status"}
    
    for table in tables:
        table_name = table[0]
        # Obtener información de columnas de la tabla
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()  # Cada fila: (cid, name, type, notnull, dflt_value, pk)
        
        for column in columns:
            col_name = column[1]
            col_type = column[2]
            
            # Se salta si la columna está en las excluidas específicas
            if col_name.lower() in columnas_excluidas:
                continue

            # Saltear la columna 'image_url' en las tablas 'items' y 'equipaments'
            if table_name in ['items', 'equipaments'] and col_name.lower() == 'image_url':
                continue
            
            # Revisamos si el tipo de columna es de texto (buscar 'char' o 'text' en el tipo)
            if col_type and ("char" in col_type.lower() or "text" in col_type.lower()):
                # Ejecutar la actualización para pasar a minúsculas. Se asegura que solo
                # se actualicen los registros donde la columna no sea nula.
                update_query = f"UPDATE {table_name} SET {col_name} = lower({col_name}) WHERE {col_name} IS NOT NULL;"
                try:
                    cursor.execute(update_query)
                    print(f"Tabla '{table_name}', columna '{col_name}' actualizada a minúsculas.")
                except sqlite3.IntegrityError as e:
                    print(f"Error actualizando {table_name}.{col_name}: {e}")
    
    conn.commit()
    conn.close()
    print("Actualización completa.")


def obtener_nombres_duplicados(db_path="data/bontar_data.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT LOWER(name) AS name_lower, GROUP_CONCAT(name) AS variantes, COUNT(*) AS cantidad
        FROM monsters
        GROUP BY name_lower
        HAVING COUNT(*) > 1
    """)
    
    duplicados = cursor.fetchall()
    conn.close()

    print("Nombres duplicados al aplicar lower():")
    for row in duplicados:
        print(f"- {row[0]} → {row[1]}")


if __name__ == "__main__":
    update_all_text_to_lowercase("data/bontar_data.db")
    obtener_nombres_duplicados()
