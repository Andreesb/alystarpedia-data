import asyncio
import time
import aiohttp
import requests
from bs4 import BeautifulSoup
import tibiapy
import random

TIBIA_CHARACTER_URL = "https://www.tibia.com/community/?subtopic=characters&name="

# Configurar headers para evitar caché
HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

session = requests.Session()
session.headers.update(HEADERS)

# Almacenar la lista de muertes y miembros en línea previos
last_deaths = {}
last_online_members = set()

async def fetch_guild_members(guild_name):
    """Obtiene los miembros en línea de una guild en Tibia mediante scraping."""
    url = f"https://www.tibia.com/community/?subtopic=guilds&page=view&GuildName={guild_name.replace(' ', '+')}"
    headers = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"❌ Error {response.status}: No se pudo obtener la página de la guild.")
                    return set()
                
                print(f"status: {response.status}")
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                
                # Buscar todos los nombres de jugadores que estén en línea
                online_members = set()
                for span in soup.find_all("span", class_="green"):
                    if span.b and span.b.text.lower() == "online":
                        name_tag = span.find_previous("a")
                        if name_tag:
                            online_members.add(name_tag.text)

                print("actualizando miembros online")
                return online_members
        
        except Exception as e:
            print(f"❌ Error al obtener la información de la guild: {e}")
            return set()


async def get_character_deaths(character_name):
    """Obtiene la lista de muertes del personaje de manera asíncrona usando un proxy."""
    global last_deaths

    url = f"{TIBIA_CHARACTER_URL}{character_name.replace(' ', '+')}"
    proxy = get_random_proxy()  # Seleccionar un proxy aleatorio

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=HEADERS, proxy=proxy) as response:
                if response.status != 200:
                    print(f"❌ Error {response.status}: No se pudo obtener la página de {character_name}.")
                    return []

                print(f"✅ Conectado con proxy {proxy} - Status: {response.status}")
                soup = BeautifulSoup(await response.text(), "html.parser")

                # Buscar la sección de Character Deaths
                deaths_section = soup.find("div", class_="Text", string="Character Deaths")
                new_deaths = []
                if deaths_section:
                    deaths_table = deaths_section.find_parent("div", class_="CaptionInnerContainer").find_next("table")
                    deaths = deaths_table.find_all("tr") if deaths_table else []

                    # Extraer muertes con fecha y descripción
                    new_deaths = [
                        (row.find_all("td")[0].text.strip(), row.find_all("td")[1].text.strip()) 
                        for row in deaths if len(row.find_all("td")) == 2
                    ]

                    if character_name not in last_deaths:
                        last_deaths[character_name] = new_deaths
                    elif len(new_deaths) > len(last_deaths[character_name]):
                        added_deaths = new_deaths[:len(new_deaths) - len(last_deaths[character_name])]
                        for date, description in added_deaths:
                            print(f"🆕 {date} - {description}")
                        last_deaths[character_name] = new_deaths
                return new_deaths

        except Exception as e:
            print(f"❌ Error con proxy {proxy}: {e}")
            return []


async def monitor_guild_deaths(guild_name, interval=10):
    """Monitorea los miembros en línea y verifica sus muertes recientes."""

    global last_online_members
    while True:
        print(f"\n🔍 Verificando miembros en línea de '{guild_name}'...")
        current_online_members = await fetch_guild_members(guild_name)
        print(current_online_members)
        
        # Si la lista de jugadores cambió, actualizarla antes de verificar muertes
        if current_online_members != last_online_members:
            print("\n🔄 Cambio detectado en la lista de miembros en línea.")
            added_members = current_online_members - last_online_members
            removed_members = last_online_members - current_online_members
            
            if added_members:
                print(f"🆕 Nuevos jugadores conectados: {', '.join(added_members)}")
            
            if removed_members:
                print(f"❌ Jugadores desconectados: {', '.join(removed_members)}")
            
            last_online_members = current_online_members  # Actualizar la lista
        
        elif (current_online_members == last_online_members):
            print(f"👥 Miembros en línea: {', '.join(current_online_members)}")
        
        for member in current_online_members:
            await get_character_deaths(member)
        
        if not current_online_members:
            print("⚠️ No hay miembros en línea en la guild.")
        
        print(f"⏳ Próxima verificación en {interval} segundos...\n")
        await asyncio.sleep(interval)

async def main():
    guild_name = input("Ingrese el nombre de la guild: ").strip()
    print(f"\n⏳ Iniciando monitoreo de la guild '{guild_name}'...\n")
    await monitor_guild_deaths(guild_name, interval=1)  # Monitorear cada 30 segundos

if __name__ == "__main__":
    asyncio.run(main())
