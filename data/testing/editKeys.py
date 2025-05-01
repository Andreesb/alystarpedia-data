import json
import os

# Ruta del archivo JSON
file_path = os.path.join("data", "database", "data", "useful", "Keys.json")

def load_keys():
    """Carga el archivo Keys.json y devuelve los datos como una lista."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_keys(data):
    """Guarda los datos actualizados en Keys.json."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print("✅ Cambios guardados correctamente.")

def find_key(keys_data, key_name):
    """Busca una llave en la lista por su atributo 'name'."""
    for item in keys_data:
        if item.get("name") == key_name:
            return item
    return None

def edit_key():
    """Permite editar palabras clave en Keys.json."""
    keys_data = load_keys()

    while True:
        # Mostrar opciones disponibles
        print("\n🔑 Lista de llaves disponibles:")
        for item in keys_data:
            print(f"- {item.get('name', 'Desconocido')}")

        # Pedir el nombre de la llave a editar
        key_name = input("\n¿Qué llave quieres editar? (Escribe el nombre exacto): ").strip()

        # Buscar la llave en la lista
        item_data = find_key(keys_data, key_name)
        if not item_data:
            print("❌ Llave no encontrada. Intenta nuevamente.")
            continue  # Volver a pedir la llave

        # Preguntar si desea agregar keywords
        add_keywords = input(f"¿Deseas agregar 'keywords' para {key_name}? (sí/no): ").strip().lower()
        if add_keywords not in ["sí", "si"]:
            print("🔙 Volviendo al inicio...")
            continue  # Volver a pedir una llave

        # Crear el atributo 'keywords' si no existe
        if "keywords" not in item_data:
            item_data["keywords"] = []

        while True:
            # Pedir palabras clave separadas por comas
            keywords_input = input("Ingrese palabras clave separadas por comas: ").strip()
            if keywords_input:
                new_keywords = [kw.strip() for kw in keywords_input.split(", ") if kw.strip()]
                item_data["keywords"].extend(new_keywords)  # Agregar palabras clave nuevas

            # Preguntar si quiere agregar más palabras clave
            another = input("¿Deseas agregar otra palabra clave? (sí/no): ").strip().lower()
            if another not in ["sí", "si"]:
                break  # Salir del bucle

        # Guardar los cambios en el JSON
        save_keys(keys_data)

        # Preguntar si quiere editar otra llave
        edit_another = input("¿Quieres editar otra llave? (sí/no): ").strip().lower()
        if edit_another not in ["sí", "si"]:
            print("👋 Saliendo del editor de llaves...")
            break  # Salir del programa

# Ejecutar la función
edit_key()
