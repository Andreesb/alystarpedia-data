import os
import sqlite3
import hashlib
from pathlib import Path

# Rutas de las carpetas
MONSTER_STATIC_DIR = Path('assets/monsters-estaticos')
BOSS_STATIC_DIR = Path('assets/bosses-estaticos')
DB_PATH = 'data/bontar_data.db'

def eliminar_duplicados_y_renombrar(carpeta):
    """
    Elimina archivos duplicados en la carpeta y renombra los archivos a minúsculas.
    """
    print(f"\nProcesando carpeta: {carpeta}")
    hashes = {}
    for archivo in carpeta.iterdir():
        if archivo.is_file():
            # Renombrar a minúsculas
            nuevo_nombre = archivo.name.lower()
            nuevo_path = carpeta / nuevo_nombre
            if archivo.name != nuevo_nombre:
                archivo.rename(nuevo_path)
                archivo = nuevo_path

            # Calcular hash del archivo
            with open(archivo, 'rb') as f:
                contenido = f.read()
                hash_archivo = hashlib.md5(contenido).hexdigest()

            # Eliminar duplicados
            if hash_archivo in hashes:
                print(f"Eliminando duplicado: {archivo}")
                archivo.unlink()
            else:
                hashes[hash_archivo] = archivo.name

def obtener_nombres_tabla(conn, tabla):
    """
    Obtiene una lista de nombres desde la tabla especificada en la base de datos.
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM {tabla}")
    return set(nombre[0].lower() for nombre in cursor.fetchall())

def eliminar_imagenes_mal_ubicadas(carpeta, nombres_validos, tipo):
    """
    Elimina imágenes que están en la carpeta incorrecta según su tipo.
    """
    print(f"\nVerificando imágenes en la carpeta: {carpeta}")
    for archivo in carpeta.iterdir():
        if archivo.is_file() and archivo.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
            nombre_archivo = archivo.stem.lower()
            if nombre_archivo not in nombres_validos:
                print(f"Eliminando imagen mal ubicada: {archivo.name}")
                archivo.unlink()

def main():
    # Paso 1: Eliminar duplicados y renombrar archivos a minúsculas
    eliminar_duplicados_y_renombrar(MONSTER_STATIC_DIR)
    eliminar_duplicados_y_renombrar(BOSS_STATIC_DIR)

    # Paso 2: Conectar a la base de datos y obtener nombres de criaturas
    conn = sqlite3.connect(DB_PATH)
    nombres_monsters = obtener_nombres_tabla(conn, 'monsters')
    nombres_bosses = obtener_nombres_tabla(conn, 'bosses')
    conn.close()

    # Paso 3: Eliminar imágenes mal ubicadas
    eliminar_imagenes_mal_ubicadas(MONSTER_STATIC_DIR, nombres_monsters, 'monster')
    eliminar_imagenes_mal_ubicadas(BOSS_STATIC_DIR, nombres_bosses, 'boss')

if __name__ == "__main__":
    main()
