import requests
from bs4 import BeautifulSoup
import json
import time

def parse_boolean(value):
    """
    Convierte "✓" a True y "✗" a False.
    """
    value = value.strip()
    if value == "✓":
        return True
    elif value == "✗":
        return False
    return value

def get_spell_links(category_url):
    """
    Extrae de la página de categoría de hechizos los enlaces a cada spell,
    buscando en TODAS las tablas con clase 'wikitable'.
    """
    response = requests.get(category_url)
    if response.status_code != 200:
        print(f"Error al obtener {category_url}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    item_links = []
    # Buscar todas las tablas con clase 'wikitable'
    tables = soup.find_all('table', class_='wikitable')
    for table in tables:
        rows = table.find_all('tr')[1:]  # Omitir encabezados
        for row in rows:
            link_tag = row.find('a', href=True)
            if link_tag:
                full_url = "https://tibia.fandom.com" + link_tag['href']
                item_links.append(full_url)
    # Eliminar duplicados (si los hay)
    return list(dict.fromkeys(item_links))

def extract_learn_from(soup):
    """
    Procesa la sección 'Learn From' extrayéndola como una lista de diccionarios.
    Se asume que la tabla tiene:
      - La primera columna: ciudad.
      - Las siguientes columnas: cada columna es una vocación (header).
      
    Para cada celda no vacía y distinta de "--", se crea un objeto:
        {
            "city": <ciudad>,
            "npc": <valor de la celda>,
            "vocation": <nombre de la vocación (según header)>
        }
    Todo se convierte a minúsculas.
    """
    trades_div = soup.find('div', class_="trades", id="twbox-learnfrom")
    learn_from_list = []
    if trades_div:
        table = trades_div.find("table", class_="wikitable")
        if table:
            header_row = table.find("tr")
            if header_row:
                headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]
            else:
                headers = []
            # Verificamos que exista al menos una columna para city y otra para vocación.
            if headers and len(headers) > 1:
                vocation_headers = headers[1:]
            else:
                vocation_headers = []
            # Procesamos cada fila (omitiendo el encabezado)
            for row in table.find_all("tr")[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 1:
                    city = cells[0].get_text(strip=True).lower()
                    # Para cada celda en las demás columnas
                    for idx, cell in enumerate(cells[1:]):
                        if idx < len(vocation_headers):
                            vocation = vocation_headers[idx]
                        else:
                            vocation = "unknown"
                        npc_val = cell.get_text(strip=True).lower()
                        if npc_val and npc_val != "--":
                            # Se crea el objeto con el valor fijo "npc" y se asigna la vocación.
                            learn_from_list.append({
                                "city": city,
                                "npc": npc_val,
                                "vocation": vocation
                            })
    return learn_from_list if learn_from_list else None

def extract_notes(soup):
    """
    Extrae la información del contenedor de Notes (texto y, opcionalmente, tabla).
    Se devuelve un diccionario con:
      - "text": concatenación de todo el texto de los párrafos.
      - "table": en caso de existir, se procesa la tabla en una lista de diccionarios.
    """
    notes_container = soup.find('div', id="twbox-notes")
    if not notes_container:
        return None

    # Texto de los párrafos
    paragraphs = notes_container.find_all('p')
    notes_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs) if paragraphs else ""

    # Procesar la tabla (si existe)
    notes_table = None
    table = notes_container.find("table", class_="wikitable")
    if table:
        header_row = table.find("tr")
        if header_row:
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(["th", "td"])]
        else:
            headers = []
        notes_table = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all(["td", "th"])
            if headers and len(cells) == len(headers):
                row_dict = { headers[i]: cells[i].get_text(" ", strip=True).lower() for i in range(len(headers)) }
                notes_table.append(row_dict)
            else:
                cell_texts = [cell.get_text(" ", strip=True).lower() for cell in cells]
                notes_table.append({"row": cell_texts})
    
    return {"text": notes_text, "table": notes_table}

def scrape_spell_data(spell_url):
    """
    Extrae la información completa de un spell:
      - Infobox: nombre, imagen y atributos (con conversión de premium/promotion).
      - Sección "Learn From": se procesa la tabla para obtener objetos con keys "city", "npc" y "vocation".
      - Sección "Notes": se extrae el contenido textual y, si existe, la tabla.
    Todo se procesa en minúsculas.
    """
    response = requests.get(spell_url)
    if response.status_code != 200:
        print(f"Error al obtener {spell_url} - código {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    spell_data = {"url": spell_url}
    
    # --- Infobox ---
    infobox = soup.find('aside', class_="portable-infobox")
    if infobox:
        # Nombre del hechizo
        title_tag = infobox.find('h2', attrs={"data-source": "name"})
        spell_data['name'] = title_tag.get_text(strip=True).lower() if title_tag else "unknown"
        
        # Imagen
        figure = infobox.find('figure', class_="pi-image")
        if figure:
            a_img = figure.find('a', class_="image")
            if a_img and a_img.has_attr('href'):
                spell_data['image_url'] = a_img['href']
            else:
                img_tag = figure.find('img')
                spell_data['image_url'] = img_tag.get('src') if img_tag else "no image"
        else:
            spell_data['image_url'] = "no image"
        
        # Atributos
        attributes = {}
        data_items = infobox.select("div.pi-item.pi-data")
        for data in data_items:
            key = data.get("data-source")
            if not key:
                label = data.find("h3", class_="pi-data-label")
                key = label.get_text(strip=True) if label else "unknown"
            value_div = data.find("div", class_="pi-data-value")
            value = value_div.get_text(" ", strip=True).lower() if value_div else ""
            if key.lower() in ["premium", "promotion"]:
                attributes[key.lower()] = parse_boolean(value)
            else:
                attributes[key.lower()] = value
        spell_data['attributes'] = attributes
    else:
        print("No se encontró la infobox en la página:", spell_url)
        spell_data['name'] = "unknown"
        spell_data['attributes'] = {}
        spell_data['image_url'] = "no image"
    
    # --- Sección "Learn From" ---
    learn_from = extract_learn_from(soup)
    spell_data['learn_from'] = learn_from if learn_from else "no learn from info"
    
    # --- Sección "Notes" ---
    notes = extract_notes(soup)
    spell_data['notes'] = notes if notes else "no notes"
    
    return spell_data

def main():
    category_url = "https://tibia.fandom.com/wiki/Spells"  # URL de la categoría de hechizos
    output_file = "Spells.json"
    
    spell_links = get_spell_links(category_url)
    all_spells_data = []
    
    print(f"Se encontraron {len(spell_links)} enlaces. Iniciando scraping...")
    for index, spell_url in enumerate(spell_links):
        print(f"Scraping ({index+1}/{len(spell_links)}): {spell_url}")
        spell_data = scrape_spell_data(spell_url)
        if spell_data:
            all_spells_data.append(spell_data)
        #time.sleep(1)  # Espera para no sobrecargar el servidor
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_spells_data, f, indent=4, ensure_ascii=False)
    
    print(f"Datos guardados en {output_file}")

if __name__ == "__main__":
    main()
