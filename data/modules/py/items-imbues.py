import os
import sqlite3
import requests

def actualizar_columnas_required_item(db_path):
    """
    Abre la base de datos, en la tabla 'imbues' agrega las columnas 'item1', 'item2' y 'item3'
    (si no existen) y actualiza cada registro dividiendo el valor en 'required_item' (separado por comas)
    en dichos campos.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verificar si las columnas ya existen; en SQLite se pueden obtener los nombres de columnas de la tabla.
    cursor.execute("PRAGMA table_info(imbues)")
    columnas = [row[1] for row in cursor.fetchall()]

    # Agregar las columnas si no existen:
    if "item1" not in columnas:
        cursor.execute("ALTER TABLE imbues ADD COLUMN item1 TEXT")
    if "item2" not in columnas:
        cursor.execute("ALTER TABLE imbues ADD COLUMN item2 TEXT")
    if "item3" not in columnas:
        cursor.execute("ALTER TABLE imbues ADD COLUMN item3 TEXT")
    conn.commit()

    # Seleccionar todos los registros de la tabla
    cursor.execute("SELECT rowid, required_item FROM imbues")
    registros = cursor.fetchall()

    for rowid, required_item in registros:
        # Si existe valor, separamos por comas
        if required_item:
            partes = [parte.strip() for parte in required_item.split(",")]
            # Asumir hasta tres elementos; si hay menos, se asignan cadenas vacías
            item1 = partes[0] if len(partes) > 0 else ""
            item2 = partes[1] if len(partes) > 1 else ""
            item3 = partes[2] if len(partes) > 2 else ""
        else:
            item1, item2, item3 = "", "", ""
        # Actualizar el registro con las nuevas columnas
        cursor.execute("""
            UPDATE imbues
            SET item1 = ?, item2 = ?, item3 = ?
            WHERE rowid = ?
        """, (item1, item2, item3, rowid))
    conn.commit()
    conn.close()
    print("Actualización de columnas de required_item completada.")

def descargar_imagenes_imbues(db_path, output_folder):
    """
    Abre la base de datos, recorre la tabla 'imbues' y descarga las imágenes de la columna
    'imbue_img_url' en la carpeta especificada, usando el valor de 'name' para generar el nombre
    del archivo.
    """
    # Crear la carpeta de destino si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT imbue_name, imbue_img_url FROM imbues")
    imbues = cursor.fetchall()
    conn.close()

    for nombre, img_url in imbues:
        if img_url and img_url.strip() != "":
            try:
                response = requests.get(img_url)
                if response.status_code == 200:
                    # Generar un nombre de archivo limpio: en minúsculas
                    nombre_archivo = nombre.strip().lower()
                    # Intentar obtener la extensión de la imagen a partir de la URL
                    _, ext = os.path.splitext(img_url)
                    if not ext:
                        ext = ".png"
                    filename = f"{nombre_archivo}{ext}"
                    filepath = os.path.join(output_folder, filename)
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    print(f"Descargada imagen para '{nombre}': {filepath}")
                else:
                    print(f"Error al descargar imagen para '{nombre}' - Código: {response.status_code}")
            except Exception as e:
                print(f"Excepción al descargar imagen para '{nombre}'. URL: {img_url}. Detalle: {e}")
        else:
            print(f"No hay URL de imagen para '{nombre}'.")

def main():
    db_path = "data/bontar_data.db"  # Reemplaza por la ruta de tu base de datos
    output_folder = "imbuements"   # Carpeta donde se descargarán las imágenes

    print("Actualizando la tabla 'imbues'...")
    actualizar_columnas_required_item(db_path)

    print("Descargando imágenes de imbues...")
    descargar_imagenes_imbues(db_path, output_folder)

if __name__ == "__main__":
    main()
