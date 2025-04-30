import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import json, time, re

IMBUING_URL = "https://tibia.fandom.com/wiki/Imbuing"
HEADERS = {"User-Agent":"imbuement-scraper/1.0"}

def fetch_soup(url):
    r = requests.get(url, headers=HEADERS); r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def parse_astral_sources(cell):
    sources = []
    for a in cell.find_all("a", href=True):
        name = a.get_text(strip=True)
        qty_node = a.previous_sibling
        if qty_node and isinstance(qty_node, (str, NavigableString)):
            m = re.search(r"(\d+)", qty_node)
            if m:
                sources.append({"item": name, "quantity": int(m.group(1))})
    return sources

def get_level_image(imbue_url):
    """Descarga la página del imbuement y devuelve la URL de su imagen principal."""
    soup = fetch_soup(imbue_url)

    # 1) Intenta obtener la imagen del infobox nuevo (portable-infobox)
    img = soup.select_one("aside.portable-infobox img")
    if img and img.has_attr("src"):
        return img["src"]

    # 2) Si no existe, busca en el formato clásico de Fandom (thumbimage)
    img = soup.find("img", class_="thumbimage")
    if img and img.has_attr("src"):
        return img["src"]

    # 3) Fallback a cualquier img dentro de .pi-image o .pi-data.pi-image
    img = soup.select_one("figure.pi-item.pi-data.pi-image img")
    if img and img.has_attr("src"):
        return img["src"]

    return None# por brevedad

def scrape_imbuements():
    soup = fetch_soup(IMBUING_URL)
    result = []

    for h4 in soup.find_all("h4"):
        span = h4.find("span", class_="mw-headline")
        if not span: continue
        category = span.get_text().strip()
        if category.lower() == "references":
            continue

        table = h4.find_next_sibling("table", class_="wikitable sortable")
        levels = {"basic":[], "intricate":[], "powerful":[]}

        if table:
            for tr in table.tbody.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 4: continue

                a = tds[0].find("a", href=True)
                name = a.get_text(strip=True)
                url  = "https://tibia.fandom.com" + a["href"]
                image_url = get_level_image(url)
                pct   = tds[1].get_text(strip=True)
                astral = parse_astral_sources(tds[2])
                avail = [x.strip() for x in tds[3].get_text().split(",")]


                low = name.lower()
                if "basic" in low:      key = "basic"
                elif "intricate" in low:key = "intricate"
                elif "powerful" in low: key = "powerful"

                levels[key].append({
                    "name": name,
                    "percentage": pct,
                    "image_url": image_url,
                    "astral_sources": astral,
                    "available_for": avail
                })

        result.append({
            "imbuement_category": category,
            "levels": levels
        })

    with open("imbuements.json","w",encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result

if __name__ == "__main__":
    data = scrape_imbuements()
    print(f"Extraídas {len(data)} categorías.")
