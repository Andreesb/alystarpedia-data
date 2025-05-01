from selenium import webdriver
import json
import time

# Configurar Selenium
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

try:
    # 1️⃣ Ir a la página de login
    driver.get("https://www.tibia.com/")
    time.sleep(5)  # Esperar manualmente para que inicies sesión

    input("⚠️ Inicia sesión manualmente y presiona ENTER aquí cuando estés listo...")

    # 2️⃣ Extraer y guardar cookies
    cookies = driver.get_cookies()
    with open("cookies.json", "w", encoding="utf-8") as file:
        json.dump(cookies, file, indent=4)

    print("✅ Cookies guardadas en cookies.json")

finally:
    driver.quit()