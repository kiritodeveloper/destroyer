from selenium import webdriver
from urllib.parse import urljoin
import time

# Configuración
driver = webdriver.Chrome()
base_url = "http://localhost:3000"
common_paths = [
    "/admin", "/backup", "/config", "/.env", "/robots.txt",
    "/.git", "/.svn", "/wp-admin", "/phpmyadmin"
]

try:
    for path in common_paths:
        full_url = urljoin(base_url, path)
        driver.get(full_url)
        time.sleep(1)
        
        # Verificar si el recurso existe
        if "404" not in driver.title and "not found" not in driver.page_source.lower():
            print(f"Directorio encontrado: {full_url}")
            # Opcional: guardar contenido
            with open("found_directories.txt", "a") as f:
                f.write(f"{full_url}\n")
    
finally:
    driver.quit()