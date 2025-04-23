import os, re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = 'https://tibia.fandom.com'
PAGE     = 'https://tibia.fandom.com/wiki/Creature_Artworks'
OUT_DIR  = 'artworks/creatures'
os.makedirs(OUT_DIR, exist_ok=True)

resp = requests.get(PAGE, timeout=10)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, 'html.parser')
        
# Ahora buscamos table con clase 'wikitable sortable'
table = soup.find(
    'table',
    attrs={'class': re.compile(r'\bwikitable\b.*\bsortable\b')}
)
if not table:
    raise RuntimeError("No se encontró la tabla 'wikitable sortable'")

for row in table.find_all('tr')[1:]:
    cols = row.find_all('td')
    if len(cols) < 3: continue

    # 1) Nombre (primer td)
    name = cols[0].get_text(strip=True)

    # 2) URL de la imagen (href de <a class="mw-file-description image">)
    link = cols[1].find('a', class_='mw-file-description image')
    if not link: 
        print(f"[SKIP] {name}: sin link de imagen")
        continue
    img_url = urljoin(BASE_URL, link['href'])

    # 3) Versión (tercer td)
    version = cols[2].get_text(strip=True)

    # 4) Extensión
    parsed = urlparse(img_url)
    m = re.search(r'\.(jpg|jpeg|png|gif)(?:\?|$)', parsed.path, re.I)
    ext = (m.group(1) if m else 'jpg').lower()

    # 5) Nombre de fichero seguro
    safe_name = re.sub(r'[^\w\-]+', '_', name)
    safe_ver  = re.sub(r'[^\d\.]+', '', version)
    filename  = f"{safe_name}_v{safe_ver}.{ext}"
    path      = os.path.join(OUT_DIR, filename)

    # 6) Descargar
    try:
        print(f"Descargando {name} v{version} → {filename}")
        img = requests.get(img_url, timeout=10)
        img.raise_for_status()
        with open(path, 'wb') as f:
            f.write(img.content)
    except Exception as e:
        print(f"[ERROR] {name} v{version}: {e}")

print("¡Listo! Todas las imágenes han sido descargadas.")
