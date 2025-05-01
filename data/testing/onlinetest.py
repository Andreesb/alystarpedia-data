import asyncio
import aiohttp
import random
from bs4 import BeautifulSoup
import json

# URL base para obtener la información de la guild
GUILD_URL = "https://www.tibia.com/community/?subtopic=guilds&page=view&GuildName="
cookies = "cookies.json"
# Lista de User-Agents para rotar
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1"
]




def load_cookies_from_file(file_path):
    """Carga las cookies desde un archivo JSON y las convierte en un diccionario."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            cookies_list = json.load(file)
        
        cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies_list}
        return cookies_dict
    except Exception as e:
        print(f"⚠️ Error al cargar cookies: {e}")
        return None


async def fetch_guild_members(guild_name, cookies_path):
    """Obtiene los miembros en línea de una guild en Tibia con autenticación."""
    url = f"{GUILD_URL}{guild_name.replace(' ', '+')}"
    
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "User-Agent": random.choice(USER_AGENTS)
    }

    # Cargar cookies desde el archivo
    cookies = load_cookies_from_file(cookies_path)
    if cookies is None:
        print("❌ No se pudieron cargar las cookies. Abortando solicitud.")
        return None

    async with aiohttp.ClientSession(cookies=cookies) as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Error {response.status}: No se pudo obtener la página de la guild.")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                # Buscar todos los jugadores en línea
                online_members = set()
                for span in soup.find_all("span"):
                    if span.b and span.b.text.lower() == "online":
                        name_tag = span.find_previous("a")
                        if name_tag:
                            # Limpia caracteres extraños como \xa0 (espacio no separable)
                            clean_name = name_tag.text.replace("\xa0", " ").strip()
                            online_members.add(clean_name)
                
                return online_members
        
        except Exception as e:
            print(f"❌ Error al obtener la información de la guild: {e}")
            return None



async def monitor_guild(guild_name, cookies_path, interval=60):
    """Monitorea en tiempo real los cambios en la lista de miembros en línea de una guild."""
    last_online_members = set()

    while True:
        print(f"🔍 Verificando miembros en línea de la guild: {guild_name}...")
        current_online_members = await fetch_guild_members(guild_name, cookies_path)
        print(f"current_online_members: {current_online_members}")

        if current_online_members is None:
            print("⚠️ No se pudo obtener la lista de miembros, intentando nuevamente en el próximo ciclo...\n")
            await asyncio.sleep(interval)
            continue

        # Si es la primera iteración, solo inicializamos la lista sin mostrar cambios
        if not last_online_members:
            last_online_members = current_online_members
            print(f"✅ Miembros en línea: {len(current_online_members)} | Esperando {interval} segundos...\n")
            await asyncio.sleep(interval)
            continue

        # Detectar nuevos miembros conectados
        new_online = current_online_members - last_online_members
        if new_online:
            for member in new_online:
                print(f"🟢 {member} se ha conectado.")

        # Detectar miembros desconectados
        disconnected = last_online_members - current_online_members
        if disconnected:
            for member in disconnected:
                print(f"🔴 {member} se ha desconectado.")

        # Actualizar la lista anterior solo si hubo un cambio real
        if new_online or disconnected:
            last_online_members = current_online_members

        print(f"✅ Miembros en línea: {len(current_online_members)} | Esperando {interval} segundos...\n")
        await asyncio.sleep(interval)  # Espera antes de la siguiente verificación

# Iniciar el monitoreo (cambiar "Nombre de la Guild" por el real)
guild_name = input("Guild name: ")
cookies_path = "cookies.json"  # Ruta al archivo de cookies
asyncio.run(monitor_guild(guild_name, cookies_path, interval=5))

