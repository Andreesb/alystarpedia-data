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
    """Permite editar, verificar y actualizar la ubicación de 'find' y 'use' en Keys.json."""
    keys_data = load_keys()
    
    while True:
        print("\n🔑 Lista de llaves disponibles:")
        for item in keys_data:
            print(f"- {item.get('name', 'Desconocido')}")
        
        key_name = input("\n¿Qué llave quieres editar? (Escribe el nombre exacto): ").strip()
        item_data = find_key(keys_data, key_name)
        if not item_data:
            print("❌ Llave no encontrada. Intenta nuevamente.")
            continue
        
        # Asegurar que location existe como diccionario
        if "location" not in item_data or not isinstance(item_data["location"], dict):
            item_data["location"] = {}
        
        # Mostrar ubicaciones actuales
        print("\n📍 Ubicaciones actuales:")
        print(f"  🔍 FIND: {item_data['location'].get('find', 'No definida')}")
        print(f"  🚪 USE: {', '.join(item_data['location'].get('use', ['No definidas']))}")
        
        # Editar ubicación 'find'
        find_location = input(f"🔍 Ingrese la nueva ubicación FIND para '{key_name}' (Enter para mantener actual): ").strip()
        if find_location:
            confirm_find = input(f"Confirme la nueva ubicación FIND ({find_location}) (sí/no): ").strip().lower()
            if confirm_find in ["sí", "si"]:
                item_data["location"]["find"] = find_location
            else:
                print("❌ Ubicación FIND descartada.")
        
        # Editar ubicaciones 'use'
        use_locations = item_data["location"].get("use", [])
        print("\n🚪 Ubicaciones USE actuales:")
        for i, loc in enumerate(use_locations, start=1):
            print(f"  {i}. {loc}")
        
        while True:
            update_option = input("¿Deseas agregar una nueva ubicación USE o modificar una existente? (agregar/modificar/no): ").strip().lower()
            
            if update_option == "agregar":
                new_use_location = input("Ingrese la nueva ubicación USE: ").strip()
                confirm_new_use = input(f"Confirme la nueva ubicación USE ({new_use_location}) (sí/no): ").strip().lower()
                if confirm_new_use in ["sí", "si"]:
                    use_locations.append(new_use_location)
                else:
                    print("❌ Ubicación USE descartada.")
            
            elif update_option == "modificar" and use_locations:
                index = int(input("Ingrese el número de la ubicación USE que desea modificar: ")) - 1
                if 0 <= index < len(use_locations):
                    new_use_location = input(f"Ingrese la nueva ubicación para {use_locations[index]}: ").strip()
                    confirm_modify_use = input(f"Confirme la nueva ubicación ({new_use_location}) (sí/no): ").strip().lower()
                    if confirm_modify_use in ["sí", "si"]:
                        use_locations[index] = new_use_location
                    else:
                        print("❌ Modificación descartada.")
                else:
                    print("❌ Número inválido.")
            
            elif update_option == "no":
                break
            else:
                print("❌ Opción no válida.")
        
        item_data["location"]["use"] = use_locations
        save_keys(keys_data)
        
        edit_another = input("¿Quieres editar otra llave? (sí/no): ").strip().lower()
        if edit_another not in ["sí", "si"]:
            print("👋 Saliendo del editor de llaves...")
            break

edit_key()
