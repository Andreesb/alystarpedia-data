import requests
from bs4 import BeautifulSoup
import json
import time

def get_item_links(category_url):
    """Obtiene los enlaces de los ítems de la categoría dada."""
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    item_links = []
    
    #para extraer la primera tabla
    table = soup.find('table', {'class': 'wikitable'})  # Obtener solo la primera tabla con la clase 'wikitable'

    if table:
        for row in table.find_all('tr')[1:]:  # Omitir el encabezado
            link_tag = row.find('a')
            if link_tag and 'href' in link_tag.attrs:
                item_links.append("https://tibia.fandom.com" + link_tag['href'])


    #para extraer la segunda tabla

    #tables = soup.find_all('table', {'class': 'wikitable'})  # Obtener todas las tablas
    #second_table = tables[1] if len(tables) > 1 else (tables[0] if tables else None)  # Segunda tabla o la única disponible
    
    #if second_table:
        #rows = second_table.find_all('tr')[1:]  # Omitir la primera fila (encabezados)
        #for row in rows:
            #link_tag = row.find('a')
            #if link_tag and 'href' in link_tag.attrs:
                #item_links.append("https://tibia.fandom.com" + link_tag['href'])


    #para extraer dos tablas

    #tables = soup.find_all('table', {'class': 'wikitable'})  # Obtener todas las tablas con la clase 'wikitable'

    #for table in tables[:2]:  # Tomar máximo 2 tablas
        #for row in table.find_all('tr')[1:]:  # Omitir el encabezado
            #link_tag = row.find('a')
            #if link_tag and 'href' in link_tag.attrs:
                #item_links.append("https://tibia.fandom.com" + link_tag['href'])


    #para extraer tres tablas

    #tables = soup.find_all('table', {'class': 'wikitable'})  # Obtener todas las tablas con la clase 'wikitable'

    #item_links = []

    #for table in tables[:3]:  # Tomar máximo 3 tablas
        #for row in table.find_all('tr')[1:]:  # Omitir el encabezado
            #link_tag = row.find('a')
            #if link_tag and 'href' in link_tag.attrs:
                #item_links.append("https://tibia.fandom.com" + link_tag['href'])

    
    return item_links

def parse_boolean(value):
    """Convierte valores de texto en booleanos según símbolos específicos."""
    return value.strip() in ['✓', 'Yes', '✗', 'No']

def scrape_item_data(item_url):
    """Extrae información detallada de un ítem."""
    response = requests.get(item_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    item_data = {"url": item_url}
    
    # Nombre del ítem
    title = soup.find('h1', {'class': 'page-header__title'})
    item_data['name'] = title.text.strip() if title else "Unknown"
    
    # Imagen del ítem
    image = soup.find('a', {'class': 'image'})
    item_data['image_url'] = image['href'] if image else "No image"
    
    # Atributos desde la caja de información
    attributes = {}
    infobox = soup.find('aside', {'class': 'portable-infobox'})
    
    if infobox:
        for data in infobox.find_all('div', {'class': 'pi-item pi-data'}):
            label = data.find('h3', {'class': 'pi-data-label'})
            value = data.find('div', {'class': 'pi-data-value'})
            
            if label and value:
                key = label.text.strip()
                val = value.text.strip()
                
                # Convertir valores booleanos
                if key in ["Stackable", "Marketable", "Pickupable", "Blocking"]:
                    attributes[key] = parse_boolean(val)
                elif key in ["Sold for", "Bought for"]:
                    attributes[key] = False if "not" in val.lower() else val
                else:
                    attributes[key] = val
    
    item_data['attributes'] = attributes
    
    # Extraer Notes
    notes_section = soup.find('div', {'id': 'creature-notes'})
    if notes_section:
        notes_text = " ".join(p.text.strip() for p in notes_section.find_all('p'))
        item_data['notes'] = notes_text if notes_text else "No notes"
    
    # Extraer Abilities
    abilities_section = soup.find('div', {'id': 'creature-abilities'})
    if abilities_section:
        abilities = []
        for ability in abilities_section.find_all('div', class_='creatureAbility'):
            ability_text = ability.get_text(strip=True, separator=" ")
            abilities.append(ability_text)
        item_data['abilities'] = abilities if abilities else ["Unknown"]

    # Extraer Resistance
    resistance_section = soup.find('div', {'id': 'creature-resistance-table'})
    if resistance_section:
        resistances = []
        for resistance in resistance_section.find_all('div', class_='creature-resistance-el'):
            resistance_text = resistance.get_text(strip=True, separator=" ")
            resistances.append(resistance_text)
        item_data['resistance'] = resistances if resistances else ["Unknown"]

    # Extraer Location
    location_section = soup.find('div', {'id': 'creature-location'})
    if location_section:
        location_text = " ".join(p.text.strip() for p in location_section.find_all('p'))
        item_data['location'] = location_text if location_text else "Unknown"

    # Extraer Behavior
    behaviour_section = soup.find('div', {'id': 'creature-behaviour'})
    if behaviour_section:
        behaviour_text = " ".join(p.text.strip() for p in behaviour_section.find_all('p'))
        item_data['behaviour'] = behaviour_text if behaviour_text else "Unknown"
    
    # Extraer strategy
    strategy_section = soup.find('div', {'id': 'creature-strategy'})
    if strategy_section:
        strategy_text = " ".join(p.text.strip() for p in strategy_section.find_all('p'))
        item_data['strategy'] = strategy_text if strategy_text else "Unknown"
    
    # Extraer Dropped By
    loot_section = soup.find('div', {'id': 'creature-loot'})
    loot = []
    if loot_section:
        for creature in loot_section.find_all('a', href=True):
            loot.append(creature.text.strip())
            item_data['loot'] = loot if loot else "This creature drops no loot."
    
    return item_data

def main():
    category_url = "https://tibia.fandom.com/wiki/Necromancers"
    output_file = "Necromancers.json"
    
    item_links = get_item_links(category_url)
    all_items_data = []
    
    for index, item_url in enumerate(item_links):
        print(f"Scraping ({index+1}/{len(item_links)}): {item_url}")
        item_data = scrape_item_data(item_url)
        all_items_data.append(item_data)

    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_items_data, f, indent=4, ensure_ascii=False)
    
    print(f"Datos guardados en {output_file}")

if __name__ == "__main__":
    main()