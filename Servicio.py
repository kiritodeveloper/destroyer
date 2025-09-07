from selenium import webdriver
import time

# Configuración
driver = webdriver.Chrome()
target_url = "http://localhost:3000"

try:
    driver.get(target_url)
    time.sleep(2)
    
    # Inyectar script que consume recursos
    malicious_js = """
    // Crear múltiples bucles infinitos
    for (let i = 0; i < 10; i++) {
        setInterval(() => {
            while(true) {
                Math.random();
            }
        }, 100);
    }
    
    // Consumir memoria
    const data = [];
    setInterval(() => {
        data.push(new Array(1000000).fill('X'));
    }, 200);
    """
    
    driver.execute_script(malicious_js)
    print("Script de consumo de recursos inyectado")
    time.sleep(10)  # Mantener ataque activo
    
finally:
    driver.quit()