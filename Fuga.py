from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configuración
driver = webdriver.Chrome()
target_url = "http://localhost:3000/search"

# Payloads para provocar errores
error_payloads = [
    "'",  # Error SQL
    "{{",  # Error de plantilla
    "<script>",  # Error XSS
    "1/0",  # Error matemático
    "admin'--"  # Error de autenticación
]

try:
    driver.get(target_url)
    time.sleep(2)
    
    for payload in error_payloads:
        search_field = driver.find_element(By.NAME, "query")
        search_field.clear()
        search_field.send_keys(payload)
        search_field.submit()
        time.sleep(2)
        
        # Analizar mensajes de error
        page_source = driver.page_source.lower()
        if any(keyword in page_source for keyword in ["sql", "syntax", "traceback", "error in", "exception"]):
            print(f"Posible fuga de información con payload: {payload}")
            with open("error_leaks.txt", "a") as f:
                f.write(f"{payload} - {driver.current_url}\n")
        
        driver.back()  # Volver al formulario
    
finally:
    driver.quit()