from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configuración
driver = webdriver.Chrome()
target_url = "http://localhost:3000/change-password"
malicious_url = "http://attacker.com/csrf-exploit"

try:
    # Simular usuario autenticado
    driver.get("http://localhost:3000/login")
    driver.find_element(By.ID, "username").send_keys("victim")
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.ID, "submit").click()
    time.sleep(2)
    
    # Visitar sitio malicioso que ejecuta acción
    driver.get(malicious_url)
    print("Sitio malicioso visitado")
    time.sleep(3)
    
    # Verificar si se ejecutó la acción
    driver.get(target_url)
    if "success" in driver.page_source:
        print("¡Ataque CSRF exitoso!")
    
finally:
    driver.quit()