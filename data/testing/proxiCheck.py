import requests
from concurrent.futures import ThreadPoolExecutor

# Lista de proxies
proxies = ['45.140.143.77:18080', '109.237.98.200:47100', '200.174.198.86:8888', '161.123.152.115:6360:qypowiof:ydruie24d3ad', '64.64.118.149:6732:qypowiof:ydruie24d3ad', '45.151.162.198:6600:qypowiof:ydruie24d3ad', '161.123.152.115:6360:nwivwuqm:zt4v4t66qkmn', '64.64.118.149:6732:nwivwuqm:zt4v4t66qkmn', '45.151.162.198:6600:nwivwuqm:zt4v4t66qkmn', '161.123.152.115:6360:imxkzbit:q52z0db5oszv', '64.64.118.149:6732:imxkzbit:q52z0db5oszv', '45.151.162.198:6600:imxkzbit:q52z0db5oszv', '161.123.152.115:6360:qjgydruw:uck90y0ysijl', '64.64.118.149:6732:qjgydruw:uck90y0ysijl', '45.151.162.198:6600:qjgydruw:uck90y0ysijl', '161.123.152.115:6360:qjgydruw:uck90y0ysijl', '64.64.118.149:6732:qjgydruw:uck90y0ysijl', '45.151.162.198:6600:qjgydruw:uck90y0ysijl', '161.123.152.115:6360:cduqwxiv:j7hrpg04yt56', '64.64.118.149:6732:cduqwxiv:j7hrpg04yt56', '45.151.162.198:6600:cduqwxiv:j7hrpg04yt56', 
'38.154.227.167:5868:qypowiof:ydruie24d3ad',
'38.153.152.244:9594:qypowiof:ydruie24d3ad',
'86.38.234.176:6630:qypowiof:ydruie24d3ad',
'173.211.0.148:6641:qypowiof:ydruie24d3ad',
'161.123.152.115:6360:qypowiof:ydruie24d3ad',
'216.10.27.159:6837:qypowiof:ydruie24d3ad',
'64.64.118.149:6732:qypowiof:ydruie24d3ad',
'104.239.105.125:6655:qypowiof:ydruie24d3ad',
'166.88.58.10:5735:qypowiof:ydruie24d3ad',
'45.151.162.198:6600:qypowiof:ydruie24d3ad',

]

# URL de prueba
TEST_URL = "https://www.tibia.com"

# Función para verificar proxy
def check_proxy(proxy):
    try:
        parts = proxy.split(":")
        
        if len(parts) == 2:  # Proxy sin autenticación (ip:port)
            ip, port = parts
            proxy_str = f"{ip}:{port}"
            proxies_dict = {
                "http": f"http://{proxy_str}",
                "https": f"http://{proxy_str}"
            }
        elif len(parts) == 4:  # Proxy con autenticación (ip:port:user:password)
            ip, port, user, password = parts
            proxy_str = f"{user}:{password}@{ip}:{port}"
            proxies_dict = {
                "http": f"http://{proxy_str}",
                "https": f"http://{proxy_str}"
            }
        else:
            print(f"⚠️ Formato incorrecto para proxy: {proxy}")
            return None
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        
        response = requests.get(TEST_URL, proxies=proxies_dict, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Proxy funcionando: {proxy}")
            return proxy
        else:
            print(f"⚠️ Proxy respondió pero con código {response.status_code}: {proxy}")
    except requests.exceptions.Timeout:
        print(f"⏳ Timeout en proxy: {proxy}")
    except requests.exceptions.ProxyError:
        print(f"🚫 Proxy inválido o bloqueado: {proxy}")
    except requests.RequestException as e:
        print(f"❌ Error desconocido en {proxy}: {e}")
    return None

# Verificar proxies en paralelo
with ThreadPoolExecutor(max_workers=10) as executor:
    working_proxies = list(filter(None, executor.map(check_proxy, proxies)))

print("\nProxies válidos:")
print(working_proxies)
