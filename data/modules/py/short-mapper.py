import json
import os
from urllib.parse import urlparse, parse_qs
from PIL import Image

# Configuración
DATA_JSON  = 'data/Keys.json'
MAPS_DIR   = 'assets/mapper/floors'
OUTPUT_DIR = 'assets/mapper/thumbnails'
REPO_BASE  = 'https://raw.githubusercontent.com/andreesb/alystarpedia-data/refs/heads/main/assets/mapper/thumbnails/'
CROP_SIZE  = 300

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carga de datos
with open(DATA_JSON, encoding='utf-8') as f:
    keys_data = json.load(f)

for key in keys_data:
    loc = key.get('location', {})
    for action in ('find', 'use'):
        urls = loc.get(action, [])
        if not isinstance(urls, list): continue 

        for idx, loc_url in enumerate(urls):
            # Extraer parámetros
            qs    = parse_qs(urlparse(loc_url).query)
            x     = int(qs.get('x', [0])[0])
            y     = int(qs.get('y', [0])[0])
            floor = int(qs.get('floor', [0])[0])
            zoom  = float(qs.get('zoom', [1.0])[0])

            # Formatear piso
            if floor >= 0:
                floor_str = f"{floor:02d}"
            else:
                floor_str = f"-{abs(floor):02d}"

            # Ruta de la imagen del piso
            path = os.path.join(MAPS_DIR, f'floor-{floor_str}-map.png')
            if not os.path.isfile(path):
                print(f"⚠️ Mapa no encontrado: {path}")
                continue

            # Cargar y recortar
            img = Image.open(path)
            cx, cy = int(x * zoom), int(y * zoom)
            half   = CROP_SIZE // 2
            left   = max(0, min(img.width  - CROP_SIZE, cx - half))
            top    = max(0, min(img.height - CROP_SIZE, cy - half))
            thumb  = img.crop((left, top, left + CROP_SIZE, top + CROP_SIZE))

            # Guardar thumbnail
            safe_name = key['name'].replace(' ', '_').replace('/', '_')
            fname     = f"{safe_name}_{action}_{idx}.png"
            outp      = os.path.join(OUTPUT_DIR, fname)
            thumb.save(outp)

            # Añadir URL al JSON
            key.setdefault('thumbnails', {}).setdefault(action, []).append(REPO_BASE + fname)

# Guardar JSON actualizado
with open('data/Keys_with_thumbs.json', 'w', encoding='utf-8') as f:
    json.dump(keys_data, f, ensure_ascii=False, indent=2)

print("✅ Thumbnails generados y Keys_with_thumbs.json actualizado.")
