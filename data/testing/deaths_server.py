import asyncio
import random
import re
import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# URLs base de Tibia
TIBIA_WORLD_URL = "https://www.tibia.com/community/?subtopic=worlds&world="
TIBIA_CHARACTER_URL = "https://www.tibia.com/community/?subtopic=characters&name="

# Lista de proxies de Webshare
PROXIES = [
    "http://p.webshare.io:80:qypowiof-1:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-2:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-3:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-4:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-5:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-6:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-7:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-8:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-9:ydruie24d3ad",
    "http://p.webshare.io:80:qypowiof-10:ydruie24d3ad"
]

# Variables globales para seguimiento de jugadores y muertes
last_online_players = set()
last_deaths = {}

def get_scraper():
    """Crea un scraper de Cloudflare con rotación de User-Agent y proxy."""
    ua = UserAgent()
    proxy = random.choice(PROXIES)
    proxy_auth = f"http://{proxy}"  # Formato requerido por cloudscraper
    scraper = cloudscraper.create_scraper()
    scraper.proxies = {"http": proxy_auth, "https": proxy_auth}
    scraper.headers.update({
        "User-Agent": ua.random,
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    })
    return scraper

def fetch_online_players(world_name):
    """Obtiene la lista de jugadores en línea de un servidor de Tibia sin caché."""
    url = f"{TIBIA_WORLD_URL}{world_name}"
    scraper = get_scraper()

    try:
        response = scraper.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        players_table = soup.find("table", class_="Table2")
        if not players_table:
            print(f"⚠️ No se encontraron jugadores en {world_name}.")
            return set()

        # Extraer nombres de jugadores, excluyendo encabezados
        players = {
            " ".join([a.text.strip() for a in row.find_all("a") if a.text.strip()])
            for row in players_table.find_all("tr", class_=["Odd", "Even"])
            if row.find("a")
        }

        print(f"👥 Jugadores en {world_name}: {len(players)}")
        return players

    except Exception as e:
        print(f"❌ Error al obtener jugadores en línea: {e}")
        return set()

def get_character_deaths(character_name):
    """Obtiene la muerte más reciente de un personaje en Tibia."""
    global last_deaths
    url = f"{TIBIA_CHARACTER_URL}{character_name.replace(' ', '+')}"
    scraper = get_scraper()

    try:
        response = scraper.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        deaths_section = soup.find("div", class_="Text", string="Character Deaths")
        if not deaths_section:
            print(f"✅ {character_name} no tiene muertes registradas.")
            return None

        deaths_table = deaths_section.find_parent("div", class_="CaptionInnerContainer").find_next("table")
        if not deaths_table:
            return None

        # Obtener la primera muerte registrada
        latest_death_row = deaths_table.find("tr")
        if not latest_death_row:
            return None

        death_cells = latest_death_row.find_all("td")
        if len(death_cells) < 2:
            return None

        raw_text = death_cells[0].text.strip()

        # Expresión regular para extraer fecha y descripción
        match = re.match(r"^(.*?CET|CETDST)(.*)$", raw_text)
        if not match:
            return None

        date = match.group(1).strip()
        most_recent_death = match.group(2).strip()

        # Comprobar si es una nueva muerte
        if character_name not in last_deaths or last_deaths[character_name][0] != date:
            last_deaths[character_name] = (date, most_recent_death)
            print(f"\n⚠️ ¡Nueva muerte detectada para {character_name}! ⚠️")
            print(f"🆕 Fecha: {date}")
            print(f"   Descripción: {most_recent_death}\n")

        return date, most_recent_death

    except Exception as e:
        print(f"❌ Error al obtener muertes de {character_name}: {e}")
        return None

async def monitor_server_deaths(world_name, interval=10):
    """Monitorea los jugadores en línea y verifica sus muertes recientes."""
    global last_online_players

    while True:
        print(f"\n🔍 Verificando jugadores en '{world_name}'...")
        current_online_players = fetch_online_players(world_name)

        # Detectar cambios en la lista de jugadores en línea
        added = current_online_players - last_online_players
        removed = last_online_players - current_online_players

        if added:
            print(f"🆕 Nuevos jugadores conectados: {', '.join(added)}")
        if removed:
            print(f"❌ Jugadores desconectados: {', '.join(removed)}")

        last_online_players = current_online_players

        # Verificar muertes solo para los jugadores en línea
        if current_online_players:
            for player in current_online_players:
                get_character_deaths(player)
        else:
            print("⚠️ No hay jugadores en línea.")

        print(f"⏳ Próxima verificación en {interval} segundos...\n")
        await asyncio.sleep(interval)

async def main():
    world_name = input("Ingrese el nombre del servidor: ").strip()
    print(f"\n⏳ Iniciando monitoreo de '{world_name}'...\n")
    await monitor_server_deaths(world_name, interval=10)

if __name__ == "__main__":
    asyncio.run(main())
